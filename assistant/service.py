from market.pricing import price_specific_board_card, price_specific_player_card, price_contract

from assistant.context import AssistantContext
from assistant.conversation_state import ConversationState
from assistant.recommender import recommendation_payload, highest_payout_payload, contract_decimal_odds
from assistant.renderer import render_response
from assistant.router import classify_query


class AssistantService:
    def __init__(self, engine, contract_manager, bettor):
        self.context = AssistantContext(engine, contract_manager, bettor)
        self.conversation = ConversationState()

    def _finalize(self, payload, intent=None, card=None, player=None):
        self.conversation.update(intent=intent, card=card, player=player)
        return render_response(payload)

    def answer(self, message: str) -> str:
        query = classify_query(message, self.conversation)
        intent = query.get("intent")
        state = self.context.state

        if intent == "empty":
            return self._finalize({"kind": "text", "text": "Ask about the pot, the board, a specific card, or which open bet looks safest or pays the most."}, intent=intent)

        if intent == "summary":
            if state is None:
                return self._finalize({"kind": "text", "text": "No hand is active right now. Start one and I can summarize the table for you."}, intent=intent)
            board = ", ".join(str(card) for card in state.community_cards) or "No community cards are out yet"
            active = [p.name for p in state.players if not p.folded]
            folded = [p.name for p in state.players if p.folded]
            payload = {
                "kind": "summary",
                "phase": self.context.engine.phase,
                "street": state.street,
                "pot": state.pot,
                "board": board,
                "active": active,
                "folded": folded,
                "bankroll": self.context.bettor.bankroll,
                "last_action": state.action_log[-1] if state.action_log else None,
            }
            return self._finalize(payload, intent=intent)

        if intent == "pot":
            if state is None:
                return self._finalize({"kind": "text", "text": "There is no active hand right now, so the pot is 0."}, intent=intent)
            return self._finalize({"kind": "text", "text": f"The pot is currently {state.pot}."}, intent=intent)

        if intent == "street":
            if state is None:
                return self._finalize({"kind": "text", "text": f"The table is idle right now."}, intent=intent)
            return self._finalize({"kind": "text", "text": f"The hand is on the {state.street}, and the engine phase is '{self.context.engine.phase}'."}, intent=intent)

        if intent == "board":
            if state is None:
                return self._finalize({"kind": "text", "text": "No hand is active right now, so there are no community cards yet."}, intent=intent)
            board = ", ".join(str(card) for card in state.community_cards) or "No community cards are out yet"
            return self._finalize({"kind": "text", "text": f"The current board is {board}."}, intent=intent)

        if intent == "active_players":
            if state is None:
                return self._finalize({"kind": "text", "text": "No hand is active right now."}, intent=intent)
            active = [p.name for p in state.players if not p.folded]
            folded = [p.name for p in state.players if p.folded]
            text = f"Still in the hand: {', '.join(active) if active else 'none'}."
            if folded:
                text += f" Folded: {', '.join(folded)}."
            return self._finalize({"kind": "text", "text": text}, intent=intent)

        if intent == "bankroll":
            bettor = self.context.bettor
            return self._finalize({"kind": "text", "text": f"You have ${bettor.bankroll:.2f} left and {len(bettor.open_bets)} open bet(s)."}, intent=intent)

        if intent == "contracts":
            contracts = self.context.open_contracts()
            payload = {
                "kind": "contracts",
                "items": [
                    {
                        "description": c.description,
                        "probability": price_contract(c, state) if state is not None else c.price,
                        "odds": contract_decimal_odds(c),
                    }
                    for c in contracts
                ]
            }
            return self._finalize(payload, intent=intent)

        if intent == "last_action":
            if state is None or not state.action_log:
                return self._finalize({"kind": "text", "text": "There is no recent table action yet."}, intent=intent)
            return self._finalize({"kind": "text", "text": f"The most recent action was: {state.action_log[-1]}"}, intent=intent)

        if intent == "board_card_probability":
            if state is None:
                return self._finalize({"kind": "text", "text": "Start a hand first so I can price board-card probability from the live public state."}, intent=intent, card=query.get("card"))
            card = query["card"]
            probability = price_specific_board_card(state, card)
            board_cards = [str(card_obj) for card_obj in state.community_cards]
            payload = {
                "kind": "board_probability",
                "card": card,
                "probability": probability,
                "board_cards": board_cards,
                "remaining_board_slots": max(0, 5 - len(state.community_cards)),
                "already_present": card in set(board_cards),
            }
            return self._finalize(payload, intent=intent, card=card)

        if intent == "player_card_probability":
            if state is None:
                return self._finalize({"kind": "text", "text": "Start a hand first so I can price player-card probability from the live public state."}, intent=intent, card=query.get("card"), player=query.get("player"))
            card = query["card"]
            player = query["player"]
            probability = price_specific_player_card(state, player, card)
            revealed_true = False
            revealed_false = False
            if self.context.engine.phase == "finished":
                target_player = next((p for p in state.players if p.name == player), None)
                if target_player is not None:
                    revealed_true = any(str(c) == card for c in target_player.hole_cards)
                    revealed_false = not revealed_true
            payload = {
                "kind": "player_probability",
                "card": card,
                "player": player,
                "probability": probability,
                "revealed_true": revealed_true,
                "revealed_false": revealed_false,
            }
            return self._finalize(payload, intent=intent, card=card, player=player)

        if intent == "recommendation":
            return self._finalize(recommendation_payload(self.context.open_contracts(), state), intent=intent)

        if intent == "highest_payout":
            return self._finalize(highest_payout_payload(self.context.open_contracts(), state), intent=intent)

        return self._finalize(
            {
                "kind": "text",
                "text": (
                    "I can help with table state, card odds, open contracts, safest bets, and highest-payout bets. "
                    "Try asking something like 'What are the chances of 4 of diamonds showing up?' or 'What pays the most right now?'"
                ),
            },
            intent="fallback",
        )
