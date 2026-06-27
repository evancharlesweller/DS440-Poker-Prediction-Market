def print_table_state(state):
    print("\n" + "=" * 60)
    print(f"STREET: {state.street.upper()} | POT: {state.pot}")
    print("BOARD:", " ".join(str(c) for c in state.community_cards) if state.community_cards else "--")
    print("-" * 60)
    for player in state.players:
        print(player)
    print("=" * 60)


def print_contracts(contracts, title="MARKET CONTRACTS"):
    print(f"\n--- {title} ---")
    for c in contracts:
        print(f"{c.contract_id:20s} | {c.description:35s} | price={c.price:.3f}")


def print_action_log(state):
    print("\n--- HAND ACTION LOG ---")
    for line in state.action_log:
        print(line)