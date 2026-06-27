from dataclasses import dataclass, field


@dataclass
class Player:
    name: str
    stack: int
    profile: str
    hole_cards: list = field(default_factory=list)
    folded: bool = False
    all_in: bool = False
    current_bet: int = 0
    total_contribution: int = 0

    def reset_for_new_hand(self):
        self.hole_cards = []
        self.folded = False
        self.all_in = False
        self.current_bet = 0
        self.total_contribution = 0

    def can_act(self) -> bool:
        return not self.folded and not self.all_in and self.stack > 0

    def commit_chips(self, amount: int) -> int:
        actual = min(amount, self.stack)
        self.stack -= actual
        self.current_bet += actual
        self.total_contribution += actual
        if self.stack == 0:
            self.all_in = True
        return actual

    def __str__(self):
        status = []
        if self.folded:
            status.append("FOLDED")
        if self.all_in:
            status.append("ALL-IN")
        status_text = f" [{' | '.join(status)}]" if status else ""
        cards = " ".join(str(c) for c in self.hole_cards) if self.hole_cards else "--"
        return f"{self.name}: stack={self.stack}, bet={self.current_bet}, cards={cards}{status_text}"