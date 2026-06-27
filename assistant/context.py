from typing import Optional


def normalize_player_name(raw_text: str) -> Optional[str]:
    if not raw_text:
        return None
    text = raw_text.strip().lower().replace(" ", "")
    if text.startswith("player"):
        suffix = text.replace("player", "", 1)
        if suffix.isdigit():
            return f"Player{int(suffix)}"
    return None


class AssistantContext:
    def __init__(self, engine, contract_manager, bettor):
        self.engine = engine
        self.contract_manager = contract_manager
        self.bettor = bettor

    @property
    def state(self):
        return self.engine.state

    def public_state_summary(self) -> str:
        state = self.state
        if state is None:
            return "No hand is currently active. Start a hand to view table state and prices."

        board = ", ".join(str(card) for card in state.community_cards) or "No community cards yet"
        active = [p.name for p in state.players if not p.folded]
        folded = [p.name for p in state.players if p.folded]
        lines = [
            f"Phase: {self.engine.phase}",
            f"Street: {state.street}",
            f"Pot: {state.pot}",
            f"Board: {board}",
            f"Active players: {', '.join(active) if active else 'None'}",
            f"Folded players: {', '.join(folded) if folded else 'None'}",
            f"{self.bettor.name} bankroll: ${self.bettor.bankroll:.2f}",
        ]
        if state.action_log:
            lines.append(f"Most recent action: {state.action_log[-1]}")
        return "\n".join(lines)

    def open_contracts(self):
        return self.contract_manager.get_open_contracts()
