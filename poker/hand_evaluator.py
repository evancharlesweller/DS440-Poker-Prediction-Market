from itertools import combinations
from collections import Counter


HAND_RANKS = {
    "high_card": 0,
    "pair": 1,
    "two_pair": 2,
    "three_kind": 3,
    "straight": 4,
    "flush": 5,
    "full_house": 6,
    "four_kind": 7,
    "straight_flush": 8,
}


def evaluate_5card_hand(cards):
    values = sorted([c.value for c in cards], reverse=True)
    suits = [c.suit for c in cards]
    counts = Counter(values)

    is_flush = len(set(suits)) == 1

    unique_vals = sorted(set(values), reverse=True)
    is_straight = False
    straight_high = None

    if len(unique_vals) == 5:
        if unique_vals[0] - unique_vals[4] == 4:
            is_straight = True
            straight_high = unique_vals[0]
        elif unique_vals == [14, 5, 4, 3, 2]:
            is_straight = True
            straight_high = 5

    sorted_counts = sorted(counts.items(), key=lambda x: (-x[1], -x[0]))
    freq_pattern = sorted(counts.values(), reverse=True)

    if is_straight and is_flush:
        return (HAND_RANKS["straight_flush"], [straight_high], "Straight Flush")

    if freq_pattern == [4, 1]:
        four = sorted_counts[0][0]
        kicker = sorted_counts[1][0]
        return (HAND_RANKS["four_kind"], [four, kicker], "Four of a Kind")

    if freq_pattern == [3, 2]:
        trips = sorted_counts[0][0]
        pair = sorted_counts[1][0]
        return (HAND_RANKS["full_house"], [trips, pair], "Full House")

    if is_flush:
        return (HAND_RANKS["flush"], values, "Flush")

    if is_straight:
        return (HAND_RANKS["straight"], [straight_high], "Straight")

    if freq_pattern == [3, 1, 1]:
        trips = sorted_counts[0][0]
        kickers = sorted([v for v, c in counts.items() if c == 1], reverse=True)
        return (HAND_RANKS["three_kind"], [trips] + kickers, "Three of a Kind")

    if freq_pattern == [2, 2, 1]:
        pairs = sorted([v for v, c in counts.items() if c == 2], reverse=True)
        kicker = [v for v, c in counts.items() if c == 1][0]
        return (HAND_RANKS["two_pair"], pairs + [kicker], "Two Pair")

    if freq_pattern == [2, 1, 1, 1]:
        pair = [v for v, c in counts.items() if c == 2][0]
        kickers = sorted([v for v, c in counts.items() if c == 1], reverse=True)
        return (HAND_RANKS["pair"], [pair] + kickers, "One Pair")

    return (HAND_RANKS["high_card"], values, "High Card")


def best_hand(seven_cards):
    best = None
    for combo in combinations(seven_cards, 5):
        rank = evaluate_5card_hand(combo)
        if best is None or rank[:2] > best[:2]:
            best = rank
    return best


def determine_winners(players, community_cards):
    ranked = []
    for player in players:
        if player.folded:
            continue
        seven_cards = player.hole_cards + community_cards
        result = best_hand(seven_cards)
        ranked.append((player, result))

    if not ranked:
        return [], None

    best_rank = max(ranked, key=lambda x: x[1][:2])[1][:2]
    winners = [player for player, rank in ranked if rank[:2] == best_rank]
    hand_name = ranked[0][1][2]
    for _, rank in ranked:
        if rank[:2] == best_rank:
            hand_name = rank[2]
            break

    return winners, hand_name