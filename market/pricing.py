from market.contracts import Contract

RANK_ALIASES = {
    'A': 'A', 'ACE': 'A',
    'K': 'K', 'KING': 'K',
    'Q': 'Q', 'QUEEN': 'Q',
    'J': 'J', 'JACK': 'J',
    'T': 'T', '10': 'T', 'TEN': 'T',
    '9': '9', 'NINE': '9',
    '8': '8', 'EIGHT': '8',
    '7': '7', 'SEVEN': '7',
    '6': '6', 'SIX': '6',
    '5': '5', 'FIVE': '5',
    '4': '4', 'FOUR': '4',
    '3': '3', 'THREE': '3',
    '2': '2', 'TWO': '2',
}

SUIT_ALIASES = {
    'S': 'Spades', 'SPADE': 'Spades', 'SPADES': 'Spades', '♠': 'Spades',
    'H': 'Hearts', 'HEART': 'Hearts', 'HEARTS': 'Hearts', '♥': 'Hearts',
    'D': 'Diamonds', 'DIAMOND': 'Diamonds', 'DIAMONDS': 'Diamonds', '♦': 'Diamonds',
    'C': 'Clubs', 'CLUB': 'Clubs', 'CLUBS': 'Clubs', '♣': 'Clubs',
}

SUIT_SYMBOLS = {
    'Spades': '♠',
    'Hearts': '♥',
    'Diamonds': '♦',
    'Clubs': '♣',
}


def _parse_rank_suit_tokens(tokens):
    if len(tokens) < 2:
        return None
    rank = RANK_ALIASES.get(tokens[0])
    suit = SUIT_ALIASES.get(tokens[1])
    if rank and suit:
        return rank, suit
    return None


def normalize_card_input(raw_text):
    if not raw_text:
        return None

    text = raw_text.strip().upper()
    text = text.replace('OF', ' ')
    text = text.replace('-', ' ')
    text = text.replace('_', ' ')
    text = ' '.join(text.split())

    if len(text) in (2, 3):
        rank_text = text[:-1]
        suit_text = text[-1]
        rank = RANK_ALIASES.get(rank_text)
        suit = SUIT_ALIASES.get(suit_text)
        if rank and suit:
            return f'{rank}{SUIT_SYMBOLS[suit]}'

    tokens = text.split()
    parsed = _parse_rank_suit_tokens(tokens)
    if parsed:
        rank, suit = parsed
        return f'{rank}{SUIT_SYMBOLS[suit]}'

    return None


def build_contracts(players):
    contracts = []

    for player in players:
        contracts.append(
            Contract(
                contract_id=f"{player.name}_wins",
                description=f"{player.name} wins the hand",
                contract_type="player_win",
                target=player.name,
                price=0.25,
            )
        )

    contracts.append(
        Contract(
            contract_id="flop_has_ace",
            description="Flop contains at least one Ace",
            contract_type="flop_has_ace",
            price=0.231,
        )
    )

    contracts.append(
        Contract(
            contract_id="showdown_occurs",
            description="The hand reaches showdown",
            contract_type="showdown_occurs",
            price=0.65,
        )
    )

    return contracts


def _public_card_strings(state):
    visible = {str(card) for card in state.community_cards}
    return visible


def price_specific_board_card(state, card_text):
    visible = _public_card_strings(state)
    if card_text in visible:
        return 1.0

    remaining_slots = max(0, 5 - len(state.community_cards))
    if remaining_slots == 0:
        return 0.0

    remaining_unseen = max(1, 52 - len(visible))
    probability = remaining_slots / remaining_unseen
    return max(0.0, min(1.0, probability))


def price_specific_player_card(state, player_name, card_text):
    visible = _public_card_strings(state)
    if card_text in visible:
        return 0.0

    player = next((p for p in state.players if p.name == player_name), None)
    if player is None:
        return 0.0

    known_hole_cards = 0
    if state.reveal_all_hole_cards:
        known_hole_cards = len(player.hole_cards)
        if any(str(card) == card_text for card in player.hole_cards):
            return 1.0
    elif state.revealed_players and player_name in state.revealed_players:
        known_hole_cards = len(player.hole_cards)
        if any(str(card) == card_text for card in player.hole_cards):
            return 1.0
        return 0.0

    unknown_hole_slots = max(0, 2 - known_hole_cards)
    if unknown_hole_slots == 0:
        return 0.0

    remaining_unseen = max(1, 52 - len(visible))
    probability = unknown_hole_slots / remaining_unseen
    return max(0.0, min(1.0, probability))


def price_contract(contract, state):
    active_players = [p for p in state.players if not p.folded]

    if contract.contract_type == 'player_win' and contract.target:
        if not active_players:
            return 0.0
        player = next((p for p in state.players if p.name == contract.target), None)
        if player is None or player.folded:
            return 0.0
        return 1 / len(active_players)

    if contract.contract_type == 'flop_has_ace':
        flop = state.community_cards[:3]
        ace_count = sum(1 for card in flop if card.rank == 'A')
        if len(flop) == 3:
            return 1.0 if ace_count > 0 else 0.0
        remaining_slots = 3 - len(flop)
        visible = _public_card_strings(state)
        unseen = max(1, 52 - len(visible))
        unseen_aces = 4 - ace_count
        if unseen_aces <= 0:
            return 1.0 if ace_count > 0 else 0.0
        no_ace_prob = 1.0
        safe_cards = unseen - unseen_aces
        for draw_index in range(remaining_slots):
            numerator = max(0, safe_cards - draw_index)
            denominator = max(1, unseen - draw_index)
            no_ace_prob *= numerator / denominator
        return 1.0 - no_ace_prob

    if contract.contract_type == 'showdown_occurs':
        alive = len(active_players)
        if alive <= 1:
            return 0.0
        return min(0.4 + 0.1 * alive, 0.95)

    if contract.contract_type == 'specific_board_card' and contract.target:
        return price_specific_board_card(state, contract.target)

    if contract.contract_type == 'specific_player_card' and contract.target_player and contract.target:
        return price_specific_player_card(state, contract.target_player, contract.target)

    return 0.0


def update_contract_prices(contracts, state):
    for contract in contracts:
        if contract.resolved:
            continue
        contract.price = round(price_contract(contract, state), 4)
