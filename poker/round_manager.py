from poker.deck import Deck
from poker.game_state import GameState
from poker.bot_profiles import decide_action
from poker.hand_evaluator import determine_winners


class RoundManager:
    def __init__(self, players, small_blind, big_blind, dealer_index=0):
        self.players = players
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.dealer_index = dealer_index

    def setup_hand(self):
        for p in self.players:
            p.reset_for_new_hand()

        deck = Deck()
        state = GameState(
            players=self.players,
            deck=deck,
            dealer_index=self.dealer_index,
            small_blind=self.small_blind,
            big_blind=self.big_blind
        )

        # deal hole cards
        for _ in range(2):
            for player in self.players:
                player.hole_cards.append(deck.draw())

        return state

    def post_blinds(self, state):
        sb_idx = (state.dealer_index + 1) % len(state.players)
        bb_idx = (state.dealer_index + 2) % len(state.players)

        sb_player = state.players[sb_idx]
        bb_player = state.players[bb_idx]

        sb_paid = sb_player.commit_chips(state.small_blind)
        bb_paid = bb_player.commit_chips(state.big_blind)

        state.pot += sb_paid + bb_paid
        state.current_bet = state.big_blind

        state.log(f"{sb_player.name} posts small blind {sb_paid}")
        state.log(f"{bb_player.name} posts big blind {bb_paid}")

    def run_betting_round(self, state, start_index):
        players = state.players
        acted = set()
        idx = start_index

        while True:
            player = players[idx]

            if player.can_act():
                to_call = state.current_bet - player.current_bet
                action, amount = decide_action(player, state, to_call)

                if action == "fold":
                    player.folded = True
                    state.log(f"{player.name} folds")

                elif action == "check":
                    state.log(f"{player.name} checks")

                elif action == "call":
                    paid = player.commit_chips(to_call)
                    state.pot += paid
                    state.log(f"{player.name} calls {paid}")

                elif action == "raise":
                    if amount <= to_call:
                        amount = to_call + state.big_blind
                    paid = player.commit_chips(amount)
                    state.pot += paid
                    state.current_bet = player.current_bet
                    acted = {idx}
                    state.log(f"{player.name} raises to {player.current_bet}")

                acted.add(idx)

                if len(state.players_in_hand()) == 1:
                    return

            idx = (idx + 1) % len(players)

            remaining = [
                i for i, p in enumerate(players)
                if not p.folded and not p.all_in
            ]

            if not remaining:
                break

            all_matched = all(
                p.folded or p.all_in or p.current_bet == state.current_bet
                for p in players
            )

            if all_matched and all(i in acted for i in remaining):
                break

    def deal_flop(self, state):
        state.deck.draw()  # burn
        state.community_cards.extend(state.deck.draw(3))
        state.street = "flop"
        state.reset_bets_for_new_street()
        state.log("Flop dealt")

    def deal_turn(self, state):
        state.deck.draw()  # burn
        state.community_cards.append(state.deck.draw())
        state.street = "turn"
        state.reset_bets_for_new_street()
        state.log("Turn dealt")

    def deal_river(self, state):
        state.deck.draw()  # burn
        state.community_cards.append(state.deck.draw())
        state.street = "river"
        state.reset_bets_for_new_street()
        state.log("River dealt")

    def showdown(self, state):
        winners, hand_name = determine_winners(state.players, state.community_cards)
        if not winners:
            return [], None

        split = state.pot // len(winners)
        for winner in winners:
            winner.stack += split

        winner_names = ", ".join(w.name for w in winners)
        state.log(f"Showdown winners: {winner_names} with {hand_name}")
        return winners, hand_name

    def award_if_only_one_left(self, state):
        active = state.players_in_hand()
        if len(active) == 1:
            winner = active[0]
            winner.stack += state.pot
            state.log(f"{winner.name} wins uncontested pot of {state.pot}")
            return winner
        return None

    def play_hand(self):
        state = self.setup_hand()
        self.post_blinds(state)

        # preflop starts left of big blind
        preflop_start = (state.dealer_index + 3) % len(state.players)
        self.run_betting_round(state, preflop_start)
        early = self.award_if_only_one_left(state)
        if early:
            self.dealer_index = (self.dealer_index + 1) % len(self.players)
            return state, [early], "Uncontested"

        # postflop starts left of dealer
        postflop_start = (state.dealer_index + 1) % len(state.players)

        self.deal_flop(state)
        self.run_betting_round(state, postflop_start)
        early = self.award_if_only_one_left(state)
        if early:
            self.dealer_index = (self.dealer_index + 1) % len(self.players)
            return state, [early], "Uncontested"

        self.deal_turn(state)
        self.run_betting_round(state, postflop_start)
        early = self.award_if_only_one_left(state)
        if early:
            self.dealer_index = (self.dealer_index + 1) % len(self.players)
            return state, [early], "Uncontested"

        self.deal_river(state)
        self.run_betting_round(state, postflop_start)
        early = self.award_if_only_one_left(state)
        if early:
            self.dealer_index = (self.dealer_index + 1) % len(self.players)
            return state, [early], "Uncontested"

        winners, hand_name = self.showdown(state)
        self.dealer_index = (self.dealer_index + 1) % len(self.players)
        return state, winners, hand_name