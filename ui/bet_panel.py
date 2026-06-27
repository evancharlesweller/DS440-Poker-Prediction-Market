from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QDoubleSpinBox,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QHBoxLayout,
    QFrame,
)


class BetPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.title_label = QLabel('Bet Slip')
        self.title_label.setStyleSheet('font-size: 18px; font-weight: 800;')
        self.available_label = QLabel('Available Bankroll: $0.00')
        self.contract_label = QLabel('Select Open Contract')
        self.contract_combo = QComboBox()
        self.contract_details = QLabel('Choose a contract to see live pricing and description.')
        self.contract_details.setWordWrap(True)

        self.stake_label = QLabel('Stake Amount')
        self.stake_input = QDoubleSpinBox()
        self.stake_input.setMinimum(1.0)
        self.stake_input.setMaximum(1000000.0)
        self.stake_input.setDecimals(2)
        self.stake_input.setValue(10.0)
        self.stake_input.setPrefix('$')

        quick_row = QHBoxLayout()
        self.quick_buttons = []
        for amount in (5, 10, 25, 50):
            btn = QPushButton(f'${amount}')
            btn.clicked.connect(lambda _, value=amount: self.stake_input.setValue(float(value)))
            self.quick_buttons.append(btn)
            quick_row.addWidget(btn)

        self.place_bet_btn = QPushButton('Place Bet')
        self.custom_card_bet_btn = QPushButton('Custom Card Bet')

        self.open_bets_label = QLabel('Open Bets')
        self.open_bets_list = QListWidget()

        card = QFrame()
        card.setObjectName('betCard')
        card_layout = QVBoxLayout()
        card_layout.addWidget(self.title_label)
        card_layout.addWidget(self.available_label)
        card_layout.addWidget(self.contract_label)
        card_layout.addWidget(self.contract_combo)
        card_layout.addWidget(self.contract_details)
        card_layout.addWidget(self.stake_label)
        card_layout.addWidget(self.stake_input)
        card_layout.addLayout(quick_row)
        card_layout.addWidget(self.place_bet_btn)
        card_layout.addWidget(self.custom_card_bet_btn)
        card_layout.addWidget(self.open_bets_label)
        card_layout.addWidget(self.open_bets_list)
        card.setLayout(card_layout)

        layout = QVBoxLayout()
        layout.addWidget(card)
        self.setLayout(layout)

        self._contracts = []
        self.contract_combo.currentIndexChanged.connect(self._update_contract_details)
        self.stake_input.valueChanged.connect(self._update_contract_details)

        self.setStyleSheet(
            '''
            QWidget { background: #0f172a; color: #edf2f7; }
            #betCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #111827, stop:1 #0f172a);
                border: 1px solid #334155;
                border-radius: 16px;
                padding: 10px;
            }
            QComboBox, QDoubleSpinBox, QListWidget {
                background: #1e293b;
                border: 1px solid #475569;
                border-radius: 8px;
                padding: 6px;
                color: #f8fafc;
            }
            QPushButton {
                background: #2563eb;
                border: none;
                border-radius: 8px;
                padding: 8px;
                color: white;
                font-weight: 700;
            }
            QPushButton:hover { background: #3b82f6; }
            '''
        )

    def set_contracts(self, contracts):
        current_id = self.current_contract_id()

        self._contracts = [c for c in contracts if c.is_open and not c.resolved]
        self.contract_combo.clear()

        for c in self._contracts:
            label = f'{c.description} | price={c.price:.3f}'
            self.contract_combo.addItem(label, c.contract_id)

        if current_id is not None:
            idx = self.contract_combo.findData(current_id)
            if idx >= 0:
                self.contract_combo.setCurrentIndex(idx)

        has_open = len(self._contracts) > 0
        self.contract_combo.setEnabled(has_open)
        self.stake_input.setEnabled(has_open)
        self.place_bet_btn.setEnabled(has_open)
        for btn in self.quick_buttons:
            btn.setEnabled(has_open)
        self._update_contract_details()

    def set_bettor_summary(self, bettor):
        self.available_label.setText(f'Available Bankroll: ${bettor.bankroll:.2f}')

    def _update_contract_details(self):
        contract_id = self.current_contract_id()
        contract = next((c for c in self._contracts if c.contract_id == contract_id), None)
        if not contract:
            self.contract_details.setText('No open contract selected.')
            return
        stake = float(self.stake_input.value())
        shares = stake / contract.price if contract.price > 0 else 0.0
        self.contract_details.setText(
            f'Description: {contract.description}\n'
            f'Live Price: {contract.price:.3f}\n'
            f'Estimated Shares: {shares:.3f}\n'
            f'Status: {contract.status_text()}'
        )

    def current_contract_id(self):
        return self.contract_combo.currentData()

    def render_open_bets(self, bettor):
        self.open_bets_list.clear()
        for bet in bettor.open_bets:
            text = (
                f'{bet.description}\n'
                f'Stake: ${bet.stake:.2f} | Entry: {bet.price:.3f} | Shares: {bet.shares:.3f}'
            )
            self.open_bets_list.addItem(QListWidgetItem(text))

    def show_error(self, message: str):
        QMessageBox.warning(self, 'Bet Error', message)

    def show_info(self, message: str):
        QMessageBox.information(self, 'Bet Placed', message)
