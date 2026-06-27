from market.contracts import Contract


def build_contracts(players):
    contracts = []

    # Player win contracts: keep open through river, close once hand ends
    for player in players:
        contracts.append(
            Contract(
                contract_id=f"{player.name}_wins",
                description=f"{player.name} wins the hand",
                contract_type="player_win",
                target=player.name,
                price=0.25,
                closes_after_street="river",
                close_immediately_on_street_reveal=False,
            )
        )

    # This should close as soon as the flop is revealed
    contracts.append(
        Contract(
            contract_id="flop_has_ace",
            description="Flop contains at least one Ace",
            contract_type="flop_has_ace",
            price=0.231,
            closes_after_street="flop",
            close_immediately_on_street_reveal=True,
        )
    )

    # Keep open until river is complete
    contracts.append(
        Contract(
            contract_id="showdown_occurs",
            description="The hand reaches showdown",
            contract_type="showdown_occurs",
            price=0.65,
            closes_after_street="river",
            close_immediately_on_street_reveal=False,
        )
    )

    return contracts


def update_contract_prices(contracts, state):
    active_players = [p for p in state.players if not p.folded]

    if active_players:
        even_price = 1 / len(active_players)
    else:
        even_price = 0.0

    for c in contracts:
        # Once resolved, keep final state
        if c.resolved:
            continue

        # Closed but unresolved: keep last quoted price frozen
        if not c.is_open:
            continue

        if c.contract_type == "player_win" and c.target:
            player = next((p for p in state.players if p.name == c.target), None)
            if player is None or player.folded:
                c.price = 0.0
            else:
                c.price = round(even_price, 3)

        elif c.contract_type == "flop_has_ace":
            if state.street == "preflop":
                c.price = 0.231
            else:
                flop = state.community_cards[:3]
                if len(flop) == 3:
                    c.price = 1.0 if any(card.rank == "A" for card in flop) else 0.0

        elif c.contract_type == "showdown_occurs":
            alive = len(active_players)
            if alive <= 1:
                c.price = 0.0
            else:
                c.price = round(min(0.4 + 0.1 * alive, 0.95), 3)