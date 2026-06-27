from poker.deck import Deck
from poker.game_state import GameState
from poker.bot_profiles import decide_action
from poker.hand_evaluator import determine_winners


class StepHandEngine:
    def __init__(self, players, small_blind, big_blind, dealer_index=0):
        self.players = players
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.dealer_index = dealer_index

        self.state = None
        self.phase = "idle"   # idle, betting, showdown, finished
        self.betting_order = []
        self.current_actor_ptr = 0
        self.acted_this_round = set()
        self.pending_postflop_start = 0
        self.winners = []
        self.hand_name = None

    def start_hand(self):
        for p in self.players:
            p.reset_for_new_hand()

        deck = Deck()
        self.state = GameState(
            players=self.players,
            deck=deck,
            dealer_index=self.dealer_index,
            small_blind=self.small_blind,
            big_blind=self.big_blind
        )

        # Deal hole cards
        for _ in range(2):
            for player in self.players:
                player.hole_cards.append(deck.draw())

        self._post_blinds()
        self.state.street = "preflop"

        # Preflop starts left of big blind
        start_idx = (self.state.dealer_index + 3) % len(self.players)
        self._begin_betting_round(start_idx)

        self.pending_postflop_start = (self.state.dealer_index + 1) % len(self.players)
        self.phase = "betting"

    def _post_blinds(self):
        sb_idx = (self.state.dealer_index + 1) % len(self.state.players)
        bb_idx = (self.state.dealer_index + 2) % len(self.state.players)

        sb_player = self.state.players[sb_idx]
        bb_player = self.state.players[bb_idx]

        sb_paid = sb_player.commit_chips(self.state.small_blind)
        bb_paid = bb_player.commit_chips(self.state.big_blind)

        self.state.pot += sb_paid + bb_paid
        self.state.current_bet = self.state.big_blind

        self.state.log(f"{sb_player.name} posts small blind {sb_paid}")
        self.state.log(f"{bb_player.name} posts big blind {bb_paid}")

    def _begin_betting_round(self, start_index):
        self.betting_order = list(range(len(self.state.players)))
        self.current_actor_ptr = start_index
        self.acted_this_round = set()

    def _only_one_left(self):
        active = [p for p in self.state.players if not p.folded]
        return len(active) == 1

    def _award_single_winner(self):
        active = [p for p in self.state.players if not p.folded]
        if len(active) == 1:
            winner = active[0]
            winner.stack += self.state.pot
            self.winners = [winner]
            self.hand_name = "Uncontested"
            self.state.reveal_all_hole_cards = True
            self.state.log(f"{winner.name} wins uncontested pot of {self.state.pot}")
            self.state.log("Hand finished: all hole cards revealed to the table view")
            self.phase = "finished"
            self.dealer_index = (self.dealer_index + 1) % len(self.players)

    def _all_bets_matched(self):
        return all(
            p.folded or p.all_in or p.current_bet == self.state.current_bet
            for p in self.state.players
        )

    def _remaining_action_indices(self):
        return [
            i for i, p in enumerate(self.state.players)
            if not p.folded and not p.all_in
        ]

    def _advance_to_next_street(self):
        if self.state.street == "preflop":
            self.state.deck.draw()  # burn
            self.state.community_cards.extend(self.state.deck.draw(3))
            self.state.street = "flop"
            self.state.log("Flop dealt")
        elif self.state.street == "flop":
            self.state.deck.draw()
            self.state.community_cards.append(self.state.deck.draw())
            self.state.street = "turn"
            self.state.log("Turn dealt")
        elif self.state.street == "turn":
            self.state.deck.draw()
            self.state.community_cards.append(self.state.deck.draw())
            self.state.street = "river"
            self.state.log("River dealt")
        elif self.state.street == "river":
            self._do_showdown()
            return

        self.state.reset_bets_for_new_street()
        self._begin_betting_round(self.pending_postflop_start)

    def _do_showdown(self):
        winners, hand_name = determine_winners(self.state.players, self.state.community_cards)
        self.winners = winners
        self.hand_name = hand_name

        if winners:
            split = self.state.pot // len(winners)
            for winner in winners:
                winner.stack += split
            names = ", ".join(w.name for w in winners)
            self.state.log(f"Showdown winners: {names} with {hand_name}")

        self.state.reveal_all_hole_cards = True
        self.state.log("Showdown complete: all hole cards revealed to the table view")
        self.phase = "finished"
        self.dealer_index = (self.dealer_index + 1) % len(self.players)

    def step(self):
        if self.phase in ("idle", "finished"):
            return

        if self._only_one_left():
            self._award_single_winner()
            return

        players = self.state.players
        searched = 0

        while searched < len(players):
            idx = self.current_actor_ptr % len(players)
            player = players[idx]

            if player.can_act():
                to_call = self.state.current_bet - player.current_bet
                action, amount = decide_action(player, self.state, to_call)

                if action == "fold":
                    player.folded = True
                    self.state.log(f"{player.name} folds")

                elif action == "check":
                    self.state.log(f"{player.name} checks")

                elif action == "call":
                    paid = player.commit_chips(to_call)
                    self.state.pot += paid
                    self.state.log(f"{player.name} calls {paid}")

                elif action == "raise":
                    if amount <= to_call:
                        amount = to_call + self.state.big_blind
                    paid = player.commit_chips(amount)
                    self.state.pot += paid
                    self.state.current_bet = player.current_bet
                    self.acted_this_round = {idx}
                    self.state.log(f"{player.name} raises to {player.current_bet}")

                self.acted_this_round.add(idx)
                self.current_actor_ptr = (idx + 1) % len(players)

                if self._only_one_left():
                    self._award_single_winner()
                    return

                remaining = self._remaining_action_indices()
                if remaining and self._all_bets_matched() and all(i in self.acted_this_round for i in remaining):
                    self._advance_to_next_street()

                return

            self.current_actor_ptr = (idx + 1) % len(players)
            searched += 1

        remaining = self._remaining_action_indices()
        if not remaining or (self._all_bets_matched() and all(i in self.acted_this_round for i in remaining)):
            self._advance_to_next_street()

    def run_to_end(self):
        while self.phase not in ("idle", "finished"):
            self.step()