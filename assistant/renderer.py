from typing import Dict, List


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def _odds(value: float) -> str:
    if value <= 0:
        return "unavailable"
    return f"{value:.2f}x"


def render_response(payload: Dict) -> str:
    kind = payload.get("kind", "text")

    if kind == "text":
        return payload.get("text", "")

    if kind == "summary":
        lines: List[str] = []
        phase = payload.get("phase")
        street = payload.get("street")
        pot = payload.get("pot")
        board = payload.get("board") or "No community cards are out yet"
        active = payload.get("active") or []
        folded = payload.get("folded") or []
        bankroll = payload.get("bankroll")
        last_action = payload.get("last_action")

        lines.append(f"The table is currently in the {street} on phase '{phase}'.")
        lines.append(f"The pot is {pot}, and the board is {board}.")
        lines.append(f"Players still in the hand: {', '.join(active) if active else 'none' }.")
        if folded:
            lines.append(f"Folded players: {', '.join(folded)}.")
        lines.append(f"Your bankroll is ${bankroll:.2f}.")
        if last_action:
            lines.append(f"Most recent action: {last_action}")
        return "\n".join(lines)

    if kind == "board_probability":
        card = payload["card"]
        probability = payload["probability"]
        board = payload.get("board_cards") or []
        remaining = payload.get("remaining_board_slots", 0)
        if payload.get("already_present"):
            return f"{card} is already on the board, so that market is effectively certain right now."
        if remaining == 0:
            return f"The board is complete and {card} never appeared, so the chance is 0% from here."
        if not board:
            return f"With no community cards out yet, {card} has about a {_pct(probability)} chance to appear on the board this hand."
        board_text = ", ".join(board)
        return (
            f"The board is {board_text}. Since {card} is not out yet and {remaining} board card"
            f"{'s' if remaining != 1 else ''} remain, it has about a {_pct(probability)} chance to appear from here."
        )

    if kind == "player_probability":
        card = payload["card"]
        player = payload["player"]
        probability = payload["probability"]
        if payload.get("revealed_true"):
            return f"The hand is over and the cards are revealed: {player} does have {card}."
        if payload.get("revealed_false"):
            return f"The hand is over and the cards are revealed: {player} does not have {card}."
        return (
            f"From the current public information, {player} has about a {_pct(probability)} chance of holding {card}. "
            "That estimate does not use hidden hole cards before showdown."
        )

    if kind == "recommendation":
        safe = payload.get("safe")
        upside = payload.get("upside")
        balanced = payload.get("balanced")
        intro = payload.get("intro")
        lines: List[str] = [intro]
        if safe:
            lines.append(
                f"Safest option: {safe['description']} — about a {_pct(safe['probability'])} hit rate and {_odds(safe['odds'])} payout."
            )
        if balanced and (not safe or balanced['description'] != safe['description']):
            lines.append(
                f"Balanced option: {balanced['description']} — around {_pct(balanced['probability'])} to hit with {_odds(balanced['odds'])} payout."
            )
        if upside:
            lines.append(
                f"Highest-upside option: {upside['description']} — lower hit rate at {_pct(upside['probability'])}, but the return is about {_odds(upside['odds'])}."
            )
        return "\n".join(lines)

    if kind == "highest_payout":
        top = payload.get("top")
        if not top:
            return "There are no open contracts to compare right now."
        return (
            f"The biggest payout available right now is {top['description']}. "
            f"It is priced like a {_pct(top['probability'])} shot, which works out to about {_odds(top['odds'])} payout."
        )

    if kind == "contracts":
        items = payload.get("items") or []
        if not items:
            return "There are no open contracts right now."
        preview = []
        for item in items[:5]:
            preview.append(
                f"• {item['description']} — {_pct(item['probability'])} implied chance, {_odds(item['odds'])} payout"
            )
        return "Here are the main open contracts right now:\n" + "\n".join(preview)

    return payload.get("text", "")
