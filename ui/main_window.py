from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
)

from config import STARTING_STACK, SMALL_BLIND, BIG_BLIND, BOT_PROFILES
from poker.player import Player
from poker.step_engine import StepHandEngine

from market.contract_manager import ContractManager
from market.bettor import Bettor

from ui.table_view import TableView
from ui.market_panel import MarketPanel
from ui.bet_panel import BetPanel
from ui.action_log_panel import ActionLogPanel
from ui.control_panel import ControlPanel
from data.auth import LocalAuthStore


class MainWindow(QMainWindow):
    def __init__(self, user_record=None, auth_store=None):
        super().__init__()
        self.user_record = user_record or {'username': 'Spectator', 'bankroll': 1000.0}
        self.auth_store = auth_store or LocalAuthStore()

        self.setWindowTitle('Poker Prediction Market')
        self.resize(1450, 900)

        self.players = self._build_players()
        self.engine = StepHandEngine(self.players, SMALL_BLIND, BIG_BLIND)

        self.contract_manager = ContractManager()
        self.contract_manager.start_new_hand(self.players)

        self.bettor = Bettor(
            name=self.user_record['username'],
            bankroll=float(self.user_record.get('bankroll', 1000.0)),
        )

        self.table_view = TableView()
        self.market_panel = MarketPanel()
        self.bet_panel = BetPanel()
        self.action_log_panel = ActionLogPanel()
        self.control_panel = ControlPanel()

        self._build_layout()
        self._wire_signals()
        self.refresh_ui()

    def _build_players(self):
        players = []
        for i, profile in enumerate(BOT_PROFILES, start=1):
            players.append(
                Player(
                    name=f'Player{i}',
                    stack=STARTING_STACK,
                    profile=profile
                )
            )
        return players

    def _build_layout(self):
        root = QWidget()
        self.setCentralWidget(root)
        self.setStyleSheet(
            '''
            QMainWindow, QWidget { background: #020617; color: #e2e8f0; }
            '''
        )

        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        right_layout = QVBoxLayout()

        top_layout.addWidget(self.table_view, 3)

        right_layout.addWidget(self.market_panel, 2)
        right_layout.addWidget(self.bet_panel, 2)

        top_layout.addLayout(right_layout, 2)

        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.action_log_panel, 1)
        main_layout.addWidget(self.control_panel)

        root.setLayout(main_layout)

    def _wire_signals(self):
        self.control_panel.new_hand_btn.clicked.connect(self.start_new_hand)
        self.control_panel.next_step_btn.clicked.connect(self.next_step)
        self.control_panel.run_to_end_btn.clicked.connect(self.run_to_end)
        self.bet_panel.place_bet_btn.clicked.connect(self.place_bet)

    def _persist_bankroll(self):
        self.auth_store.save_bankroll(self.bettor.name, self.bettor.bankroll)

    def start_new_hand(self):
        self.contract_manager.start_new_hand(self.players)
        self.engine.start_hand()
        self.contract_manager.update_for_state(self.engine.state)
        self.refresh_ui()

    def next_step(self):
        if self.engine.phase == 'idle':
            return

        self.engine.step()

        if self.engine.state is not None:
            self.contract_manager.update_for_state(self.engine.state)

        if self.engine.phase == 'finished':
            self._settle_market()

        self.refresh_ui()

    def run_to_end(self):
        if self.engine.phase == 'idle':
            return

        self.engine.run_to_end()

        if self.engine.state is not None:
            self.contract_manager.update_for_state(self.engine.state)

        if self.engine.phase == 'finished':
            self._settle_market()

        self.refresh_ui()

    def place_bet(self):
        contract_id = self.bet_panel.current_contract_id()
        stake = float(self.bet_panel.stake_input.value())

        if contract_id is None:
            self.bet_panel.show_error('No open contract selected.')
            return

        contract = next(
            (c for c in self.contract_manager.get_contracts() if c.contract_id == contract_id),
            None
        )
        if contract is None:
            self.bet_panel.show_error('Selected contract was not found.')
            return

        try:
            bet = self.bettor.place_bet(contract, stake)
        except ValueError as e:
            self.bet_panel.show_error(str(e))
            return

        self._persist_bankroll()
        self.bet_panel.show_info(
            f"Placed bet on '{bet.contract_id}'\n"
            f'Stake: {bet.stake:.2f}\n'
            f'Price: {bet.price:.3f}\n'
            f'Shares: {bet.shares:.3f}'
        )

        self.refresh_ui()

    def _settle_market(self):
        self.contract_manager.settle(
            self.engine.state,
            self.engine.winners,
            self.engine.hand_name
        )

        contracts_by_id = {
            c.contract_id: c for c in self.contract_manager.get_contracts()
        }
        self.bettor.settle_bets(contracts_by_id)
        self._persist_bankroll()

    def refresh_ui(self):
        state = self.engine.state
        contracts = self.contract_manager.get_contracts()

        self.table_view.render_state(state, self.engine.phase)
        self.market_panel.render_contracts(contracts)
        self.market_panel.render_bankroll(self.bettor)
        self.market_panel.render_settled_bets(self.bettor)

        self.bet_panel.set_contracts(contracts)
        self.bet_panel.set_bettor_summary(self.bettor)
        self.bet_panel.render_open_bets(self.bettor)

        self.action_log_panel.render_log(state.action_log if state else [])
        self.control_panel.render_status(self.engine.phase, self.bettor.name)
