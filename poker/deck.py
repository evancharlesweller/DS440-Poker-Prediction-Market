import random
from poker.cards import Card, SUITS, RANKS


class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for suit in SUITS for rank in RANKS]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, n=1):
        if n == 1:
            return self.cards.pop()
        return [self.cards.pop() for _ in range(n)]