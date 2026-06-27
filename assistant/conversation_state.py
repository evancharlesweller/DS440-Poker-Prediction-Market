from typing import Optional


class ConversationState:
    def __init__(self):
        self.last_intent: Optional[str] = None
        self.last_card: Optional[str] = None
        self.last_player: Optional[str] = None

    def update(self, intent: Optional[str] = None, card: Optional[str] = None, player: Optional[str] = None):
        if intent:
            self.last_intent = intent
        if card:
            self.last_card = card
        if player:
            self.last_player = player
