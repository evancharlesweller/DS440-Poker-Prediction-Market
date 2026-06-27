from dataclasses import dataclass, field


@dataclass
class Bet:
    contract_id: str
    description: str
    stake: float
    price: float
    shares: float
    resolved: bool = False
    won: bool | None = None
    payout: float = 0.0


@dataclass
class Bettor:
    name: str
    bankroll: float
    open_bets: list = field(default_factory=list)
    settled_bets: list = field(default_factory=list)

    def can_afford(self, amount: float) -> bool:
        return amount > 0 and self.bankroll >= amount

    def place_bet(self, contract, stake: float):
        if stake <= 0:
            raise ValueError("Stake must be greater than 0.")
        if contract.resolved:
            raise ValueError("Cannot bet on a resolved contract.")
        if contract.price <= 0:
            raise ValueError("Contract price must be greater than 0.")
        if self.bankroll < stake:
            raise ValueError("Insufficient bankroll.")

        shares = stake / contract.price

        self.bankroll -= stake

        bet = Bet(
            contract_id=contract.contract_id,
            description=contract.description,
            stake=round(stake, 2),
            price=round(contract.price, 4),
            shares=round(shares, 4),
        )
        self.open_bets.append(bet)
        return bet

    def settle_bets(self, contracts_by_id: dict):
        remaining_open = []

        for bet in self.open_bets:
            contract = contracts_by_id.get(bet.contract_id)

            if contract is None or not contract.resolved:
                remaining_open.append(bet)
                continue

            bet.resolved = True
            bet.won = bool(contract.outcome)

            if bet.won:
                payout = bet.shares * 1.0
            else:
                payout = 0.0

            bet.payout = round(payout, 2)
            self.bankroll += bet.payout
            self.settled_bets.append(bet)

        self.open_bets = remaining_open