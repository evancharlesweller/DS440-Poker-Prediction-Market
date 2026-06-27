def settle_contracts(contracts, state, winners, hand_name):
    winner_names = {w.name for w in winners} if winners else set()
    showdown_happened = hand_name != 'Uncontested'
    board_text = {str(card) for card in state.community_cards}

    for contract in contracts:
        if contract.contract_type == 'player_win':
            contract.outcome = contract.target in winner_names

        elif contract.contract_type == 'flop_has_ace':
            flop = state.community_cards[:3]
            contract.outcome = any(card.rank == 'A' for card in flop)

        elif contract.contract_type == 'showdown_occurs':
            contract.outcome = showdown_happened

        elif contract.contract_type == 'specific_board_card':
            contract.outcome = contract.target in board_text

        elif contract.contract_type == 'specific_player_card':
            player = next((p for p in state.players if p.name == contract.target_player), None)
            contract.outcome = bool(player and any(str(card) == contract.target for card in player.hole_cards))

        else:
            contract.outcome = False

        contract.resolved = True
        contract.is_open = False
