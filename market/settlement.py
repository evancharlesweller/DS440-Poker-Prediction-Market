def settle_contracts(contracts, state, winners, hand_name):
    winner_names = {w.name for w in winners} if winners else set()
    showdown_happened = hand_name != "Uncontested"

    for c in contracts:
        if c.contract_type == "player_win":
            c.outcome = c.target in winner_names

        elif c.contract_type == "flop_has_ace":
            flop = state.community_cards[:3]
            c.outcome = any(card.rank == "A" for card in flop)

        elif c.contract_type == "showdown_occurs":
            c.outcome = showdown_happened

        else:
            c.outcome = False

        c.resolved = True
        c.is_open = False