from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QFrame
)
from PyQt5.QtGui import QColor


class MarketPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.title_label = QLabel('Prediction Market')
        self.title_label.setStyleSheet('font-size: 18px; font-weight: 800;')
        self.bankroll_label = QLabel('Spectator Bankroll: 1000.00')
        self.market_summary_label = QLabel('Open Contracts: 0 | Resolved: 0')
        self.contract_list = QListWidget()
        self.settled_bets_label = QLabel('Settled Bets')
        self.settled_bets_list = QListWidget()

        card = QFrame()
        card.setObjectName('marketCard')
        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.bankroll_label)
        layout.addWidget(self.market_summary_label)
        layout.addWidget(self.contract_list)
        layout.addWidget(self.settled_bets_label)
        layout.addWidget(self.settled_bets_list)
        card.setLayout(layout)

        root = QVBoxLayout()
        root.addWidget(card)
        self.setLayout(root)

        self.setStyleSheet(
            '''
            QWidget { background: #0f172a; color: #edf2f7; }
            #marketCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f172a, stop:1 #111827);
                border: 1px solid #334155;
                border-radius: 16px;
                padding: 10px;
            }
            QListWidget {
                background: #1e293b;
                border: 1px solid #475569;
                border-radius: 8px;
                padding: 6px;
                color: #f8fafc;
            }
            QLabel {
                color: #e2e8f0;
            }
            '''
        )

    def render_contracts(self, contracts):
        self.contract_list.clear()
        open_count = sum(1 for c in contracts if c.is_open and not c.resolved)
        resolved_count = sum(1 for c in contracts if c.resolved)
        self.market_summary_label.setText(
            f'Open Contracts: {open_count} | Resolved: {resolved_count}'
        )

        for c in contracts:
            status = c.status_text()
            outcome_text = ''
            if c.resolved:
                outcome_text = ' | YES' if c.outcome else ' | NO'

            text = (
                f'[{status}] {c.description}\n'
                f'Contract: {c.contract_id} | Price: {c.price:.3f}{outcome_text}'
            )
            item = QListWidgetItem(text)
            if c.resolved:
                item.setForeground(QColor('#93c5fd' if c.outcome else '#fca5a5'))
            elif c.is_open:
                item.setForeground(QColor('#86efac'))
            else:
                item.setForeground(QColor('#fcd34d'))
            self.contract_list.addItem(item)

    def render_bankroll(self, bettor):
        self.bankroll_label.setText(f'{bettor.name} Bankroll: ${bettor.bankroll:.2f}')

    def render_settled_bets(self, bettor):
        self.settled_bets_list.clear()
        for bet in bettor.settled_bets:
            result = 'WIN' if bet.won else 'LOSS'
            text = (
                f'[{result}] {bet.description}\n'
                f'Stake: ${bet.stake:.2f} | Payout: ${bet.payout:.2f}'
            )
            item = QListWidgetItem(text)
            item.setForeground(QColor('#86efac' if bet.won else '#fca5a5'))
            self.settled_bets_list.addItem(item)
