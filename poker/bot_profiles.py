import random


def preflop_strength(hole_cards) -> int:
    ranks = sorted([c.value for c in hole_cards], reverse=True)
    suited = hole_cards[0].suit == hole_cards[1].suit
    pair = ranks[0] == ranks[1]

    score = sum(ranks)

    if pair:
        score += 20
    if suited:
        score += 3
    if abs(ranks[0] - ranks[1]) == 1:
        score += 2
    if ranks[0] >= 13:
        score += 2

    return score


def decide_action(player, game_state, to_call: int):
    """
    Returns tuple: (action, amount)
    action in {"fold", "check", "call", "raise"}
    amount is raise total contribution for this action round, not total table bet.
    """
    strength = preflop_strength(player.hole_cards)
    profile = player.profile

    if game_state.street != "preflop":
        # Very simple postflop logic for MVP
        strength += random.randint(-3, 6)

    if profile == "tight_passive":
        if to_call == 0:
            if strength >= 32 and random.random() < 0.2:
                return "raise", max(game_state.big_blind, 20)
            return "check", 0
        if strength >= 36:
            return "call", to_call
        return "fold", 0

    if profile == "loose_aggressive":
        if strength >= 28 and random.random() < 0.45:
            return "raise", max(game_state.big_blind * 2, to_call + 20)
        if to_call == 0:
            return "check", 0
        if strength >= 22:
            return "call", to_call
        return "fold", 0

    if profile == "balanced":
        if strength >= 35 and random.random() < 0.3:
            return "raise", max(game_state.big_blind * 2, to_call + 15)
        if to_call == 0:
            return "check", 0
        if strength >= 26:
            return "call", to_call
        return "fold", 0

    # random profile
    if to_call == 0:
        return random.choice([("check", 0), ("raise", max(game_state.big_blind, 15))])
    return random.choice([("fold", 0), ("call", to_call)])