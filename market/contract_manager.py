from market.pricing import build_contracts, update_contract_prices
from market.settlement import settle_contracts


STREET_ORDER = {
    "preflop": 0,
    "flop": 1,
    "turn": 2,
    "river": 3,
}


class ContractManager:
    def __init__(self):
        self.contracts = []

    def start_new_hand(self, players):
        self.contracts = build_contracts(players)

    def get_contracts(self):
        return self.contracts

    def get_open_contracts(self):
        return [c for c in self.contracts if c.is_open and not c.resolved]

    def update_for_state(self, state):
        if state is None:
            return

        self._apply_closure_rules(state)
        update_contract_prices(self.contracts, state)

    def settle(self, state, winners, hand_name):
        settle_contracts(self.contracts, state, winners, hand_name)

    def _apply_closure_rules(self, state):
        current_street = state.street

        for contract in self.contracts:
            if contract.resolved or not contract.is_open:
                continue

            close_street = contract.closes_after_street

            if close_street is None:
                continue

            if contract.close_immediately_on_street_reveal:
                # Example: flop event contracts should close as soon as flop is revealed
                if current_street == close_street:
                    contract.is_open = False
            else:
                # Example: contracts that remain open through a street but not after
                current_order = STREET_ORDER.get(current_street, -1)
                close_order = STREET_ORDER.get(close_street, 99)
                if current_order > close_order:
                    contract.is_open = False