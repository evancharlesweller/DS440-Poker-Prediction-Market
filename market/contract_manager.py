from market.pricing import build_contracts, update_contract_prices
from market.settlement import settle_contracts


class ContractManager:
    def __init__(self):
        self.contracts = []

    def start_new_hand(self, players):
        self.contracts = build_contracts(players)

    def get_contracts(self):
        return self.contracts

    def get_open_contracts(self):
        return [c for c in self.contracts if c.is_open and not c.resolved]

    def find_contract(self, contract_id):
        return next((c for c in self.contracts if c.contract_id == contract_id), None)

    def add_contract(self, contract):
        existing = self.find_contract(contract.contract_id)
        if existing is None:
            self.contracts.append(contract)
            return contract
        return existing

    def update_for_state(self, state):
        if state is None:
            return
        update_contract_prices(self.contracts, state)

    def settle(self, state, winners, hand_name):
        settle_contracts(self.contracts, state, winners, hand_name)
