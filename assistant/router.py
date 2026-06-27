import re
from typing import Dict, Optional

from market.pricing import normalize_card_input


CARD_WORD_RE = re.compile(
    r"\b(ace|king|queen|jack|ten|[2-9]|10)\s+of\s+(spades?|hearts?|diamonds?|clubs?)\b",
    flags=re.IGNORECASE,
)
SHORT_CARD_RE = re.compile(r"\b(10|[2-9AJQKT])\s*([shdc♠♥♦♣])\b", flags=re.IGNORECASE)
PLAYER_RE = re.compile(r"player\s*(\d+)", flags=re.IGNORECASE)


FOLLOWUP_PHRASES = {
    "what about",
    "how about",
    "and the",
    "what if",
}


def _extract_player_name(text: str) -> Optional[str]:
    match = PLAYER_RE.search(text)
    if match:
        return f"Player{int(match.group(1))}"
    return None


def _extract_card(text: str) -> Optional[str]:
    direct = normalize_card_input(text)
    if direct:
        return direct

    word_match = CARD_WORD_RE.search(text)
    if word_match:
        return normalize_card_input(f"{word_match.group(1)} of {word_match.group(2)}")

    short_match = SHORT_CARD_RE.search(text)
    if short_match:
        return normalize_card_input("".join(short_match.groups()))

    return None


def _is_followup(lowered: str) -> bool:
    return any(lowered.startswith(prefix) for prefix in FOLLOWUP_PHRASES)


def classify_query(message: str, conversation_state=None) -> Dict[str, str]:
    text = (message or "").strip()
    lowered = text.lower()

    if not text:
        return {"intent": "empty"}

    player_name = _extract_player_name(text)
    card = _extract_card(text)

    if not card and conversation_state is not None and _is_followup(lowered):
        card = conversation_state.last_card
    if not player_name and conversation_state is not None and _is_followup(lowered):
        player_name = conversation_state.last_player

    if any(phrase in lowered for phrase in ["highest payout", "biggest payout", "most payout", "longest odds"]):
        return {"intent": "highest_payout"}

    if any(phrase in lowered for phrase in ["best bet", "best bets", "recommend", "should i buy", "what should i buy", "safest bet"]):
        return {"intent": "recommendation"}

    if any(word in lowered for word in ["chance", "chances", "odds", "probability", "likely"]):
        if card and player_name and any(word in lowered for word in ["hand", "hold", "has"]):
            return {"intent": "player_card_probability", "card": card, "player": player_name}
        if card and any(word in lowered for word in ["board", "table", "community", "show up", "appear", "there is", "there's"]):
            return {"intent": "board_card_probability", "card": card}
        if card and player_name:
            return {"intent": "player_card_probability", "card": card, "player": player_name}
        if card:
            return {"intent": "board_card_probability", "card": card}

    if any(word in lowered for word in ["summarize", "summary", "game state", "table state"]):
        return {"intent": "summary"}
    if "pot" in lowered:
        return {"intent": "pot"}
    if any(word in lowered for word in ["street", "phase"]):
        return {"intent": "street"}
    if "board" in lowered or "community cards" in lowered:
        return {"intent": "board"}
    if any(word in lowered for word in ["active", "still in", "who is in"]):
        return {"intent": "active_players"}
    if any(word in lowered for word in ["bankroll", "balance", "cash"]):
        return {"intent": "bankroll"}
    if any(word in lowered for word in ["open contracts", "markets", "contracts"]):
        return {"intent": "contracts"}
    if any(word in lowered for word in ["last action", "recent action", "what happened"]):
        return {"intent": "last_action"}

    if card and player_name:
        base_intent = "player_card_probability"
        if conversation_state is not None and conversation_state.last_intent == "board_card_probability":
            base_intent = "board_card_probability"
        if base_intent == "player_card_probability":
            return {"intent": base_intent, "card": card, "player": player_name}
        return {"intent": base_intent, "card": card}
    if card:
        if conversation_state is not None and conversation_state.last_intent == "player_card_probability" and conversation_state.last_player:
            return {"intent": "player_card_probability", "card": card, "player": conversation_state.last_player}
        return {"intent": "board_card_probability", "card": card}

    return {"intent": "fallback", "raw": text}
