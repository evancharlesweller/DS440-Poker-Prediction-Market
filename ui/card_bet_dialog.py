from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QLineEdit,
    QDoubleSpinBox, QPushButton, QMessageBox, QHBoxLayout, QFrame
)

from market.pricing import (
    normalize_card_input,
    price_specific_board_card,
    price_specific_player_card,
)


class CardBetDialog(QDialog):
    def __init__(self, players, state, parent=None):
        super().__init__(parent)
        self.players = players
        self.state = state
        self._result_payload = None

        self.setWindowTitle('Custom Card Bet')
        self.resize(520, 420)

        self.title_label = QLabel('Create a Custom Card Market')
        self.title_label.setStyleSheet('font-size: 18px; font-weight: 800; color: #f8fafc;')

        self.help_label = QLabel(
            'Pure-probability pricing only. Bets stay open for the full hand and exact hole cards are only revealed at showdown.'
        )
        self.help_label.setWordWrap(True)
        self.help_label.setStyleSheet('color: #cbd5e1;')

        self.type_combo = QComboBox()
        self.type_combo.addItem('Specific card appears on the board', 'specific_board_card')
        self.type_combo.addItem('Specific card is in a player hand', 'specific_player_card')

        self.player_combo = QComboBox()
        for player in players:
            self.player_combo.addItem(player.name, player.name)

        self.card_input = QLineEdit()
        self.card_input.setPlaceholderText('Examples: 4d, A♠, ace of spades')

        self.normalized_label = QLabel('Normalized Card: --')
        self.normalized_label.setStyleSheet('color: #93c5fd; font-weight: 700;')

        self.stake_input = QDoubleSpinBox()
        self.stake_input.setMinimum(1.0)
        self.stake_input.setMaximum(1000000.0)
        self.stake_input.setDecimals(2)
        self.stake_input.setValue(10.0)
        self.stake_input.setPrefix('$')

        self.preview_card = QFrame()
        self.preview_card.setObjectName('previewCard')
        preview_layout = QVBoxLayout()
        preview_layout.setContentsMargins(10, 10, 10, 10)
        self.preview_label = QLabel('Enter a card to see pure-probability pricing.')
        self.preview_label.setWordWrap(True)
        preview_layout.addWidget(self.preview_label)
        self.preview_card.setLayout(preview_layout)

        self.cancel_btn = QPushButton('Cancel')
        self.confirm_btn = QPushButton('Create Bet')

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(self.cancel_btn)
        buttons.addWidget(self.confirm_btn)

        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.help_label)
        layout.addWidget(QLabel('Bet Type'))
        layout.addWidget(self.type_combo)
        self.player_label = QLabel('Target Player')
        layout.addWidget(self.player_label)
        layout.addWidget(self.player_combo)
        layout.addWidget(QLabel('Card'))
        layout.addWidget(self.card_input)
        layout.addWidget(self.normalized_label)
        layout.addWidget(QLabel('Stake'))
        layout.addWidget(self.stake_input)
        layout.addWidget(self.preview_card)
        layout.addLayout(buttons)
        self.setLayout(layout)

        self.type_combo.currentIndexChanged.connect(self._update_preview)
        self.player_combo.currentIndexChanged.connect(self._update_preview)
        self.card_input.textChanged.connect(self._update_preview)
        self.stake_input.valueChanged.connect(self._update_preview)
        self.cancel_btn.clicked.connect(self.reject)
        self.confirm_btn.clicked.connect(self._confirm)

        self.setStyleSheet(
            '''
            QDialog { background: #0f172a; color: #edf2f7; }
            QComboBox, QLineEdit, QDoubleSpinBox {
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
                padding: 8px 12px;
                color: white;
                font-weight: 700;
            }
            QPushButton:hover { background: #3b82f6; }
            #previewCard {
                background: #111827;
                border: 1px solid #334155;
                border-radius: 12px;
            }
            '''
        )

        self._update_preview()

    def _selected_contract_type(self):
        return self.type_combo.currentData()

    def _selected_player(self):
        return self.player_combo.currentData()

    def _compute_preview(self):
        card_text = normalize_card_input(self.card_input.text())
        if not card_text:
            return None

        contract_type = self._selected_contract_type()
        if contract_type == 'specific_board_card':
            probability = price_specific_board_card(self.state, card_text)
            description = f'{card_text} appears among the community cards'
            contract_id = f'board_card::{card_text}'
            target_player = None
        else:
            player_name = self._selected_player()
            probability = price_specific_player_card(self.state, player_name, card_text)
            description = f'{player_name} holds {card_text}'
            contract_id = f'player_card::{player_name}::{card_text}'
            target_player = player_name

        stake = float(self.stake_input.value())
        shares = (stake / probability) if probability > 0 else 0.0
        return {
            'contract_type': contract_type,
            'contract_id': contract_id,
            'description': description,
            'target': card_text,
            'target_player': target_player,
            'price': round(probability, 4),
            'stake': round(stake, 2),
            'shares': round(shares, 4),
        }

    def _update_preview(self):
        is_player_market = self._selected_contract_type() == 'specific_player_card'
        self.player_label.setVisible(is_player_market)
        self.player_combo.setVisible(is_player_market)

        normalized = normalize_card_input(self.card_input.text())
        self.normalized_label.setText(f'Normalized Card: {normalized if normalized else "--"}')

        payload = self._compute_preview()
        if payload is None:
            self.preview_label.setText(
                'Invalid card input. Use forms like 4d, Td, A♠, or ace of spades.\n\n'
                'Examples:\n'
                '• Board market: 4♦ appears among the community cards\n'
                '• Player market: Player2 holds A♠'
            )
            return

        probability = payload['price']
        implied_payout = (1.0 / probability) if probability > 0 else 0.0

        if probability <= 0:
            edge_text = 'This contract is currently impossible from public information, so it cannot be bought.'
        elif probability >= 1.0:
            edge_text = 'This contract is already certain from public information. It stays listed, but there is no upside in buying it now.'
        else:
            edge_text = 'Market stays open until hand resolution; pricing is pure probability from public information only.'

        self.preview_label.setText(
            f"Contract: {payload['description']}\n"
            f"Pure Probability Price: {probability:.4f}\n"
            f"Implied Decimal Payout: {implied_payout:.2f}x\n"
            f"Estimated Shares: {payload['shares']:.3f}\n\n"
            f"{edge_text}"
        )

    def _confirm(self):
        payload = self._compute_preview()
        if payload is None:
            QMessageBox.warning(self, 'Invalid Card', 'Please enter a valid card.')
            return
        if payload['price'] <= 0:
            QMessageBox.warning(
                self,
                'Unbuyable Market',
                'This market is currently impossible from public information, so it cannot be bought.'
            )
            return
        self._result_payload = payload
        self.accept()

    def result_payload(self):
        return self._result_payload
