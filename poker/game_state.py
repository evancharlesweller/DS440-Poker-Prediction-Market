from dataclasses import dataclass, field


@dataclass
class GameState:
    players: list
    deck: object
    dealer_index: int
    small_blind: int
    big_blind: int
    pot: int = 0
    community_cards: list = field(default_factory=list)
    street: str = "preflop"
    current_bet: int = 0
    action_log: list = field(default_factory=list)
    reveal_all_hole_cards: bool = False
    revealed_players: set = field(default_factory=set)

    def reset_bets_for_new_street(self):
        self.current_bet = 0
        for player in self.players:
            player.current_bet = 0

    def active_players(self):
        return [p for p in self.players if not p.folded]

    def players_in_hand(self):
        return [p for p in self.players if not p.folded]

    def next_index(self, idx: int) -> int:
        return (idx + 1) % len(self.players)

    def log(self, message: str):
        self.action_log.append(message)