from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QGridLayout,
)
from PyQt5.QtCore import Qt


RED_SUITS = {'♥', '♦'}


def card_style(card_text: str) -> str:
    is_red = any(s in card_text for s in RED_SUITS)
    color = '#b91c1c' if is_red else '#111827'
    return (
        'background: #f8fafc; '
        f'color: {color}; '
        'border: 2px solid #cbd5e1; '
        'border-radius: 10px; '
        'font-size: 18px; '
        'font-weight: 800;'
    )


class PlayerSeat(QFrame):
    def __init__(self, seat_name: str):
        super().__init__()
        self.setObjectName('seatCard')

        self.top_row = QHBoxLayout()
        self.top_row.setContentsMargins(0, 0, 0, 0)

        self.dealer_badge = QLabel('D')
        self.dealer_badge.setAlignment(Qt.AlignCenter)
        self.dealer_badge.setObjectName('dealerBadge')
        self.dealer_badge.hide()

        self.role_badge = QLabel('--')
        self.role_badge.setAlignment(Qt.AlignCenter)
        self.role_badge.setObjectName('roleBadge')
        self.role_badge.hide()

        self.top_row.addWidget(self.dealer_badge)
        self.top_row.addStretch(1)
        self.top_row.addWidget(self.role_badge)

        self.avatar_label = QLabel('●')
        self.avatar_label.setAlignment(Qt.AlignCenter)
        self.avatar_label.setObjectName('avatarLabel')

        self.name_label = QLabel(seat_name)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet('font-size: 15px; font-weight: 700;')

        self.cards_label = QLabel('🂠  🂠')
        self.cards_label.setAlignment(Qt.AlignCenter)
        self.cards_label.setObjectName('holeCardsLabel')

        self.stack_chip = QLabel('Stack  --')
        self.stack_chip.setAlignment(Qt.AlignCenter)
        self.stack_chip.setObjectName('chipBadge')

        self.bet_chip = QLabel('Live Bet  --')
        self.bet_chip.setAlignment(Qt.AlignCenter)
        self.bet_chip.setObjectName('chipBadgeBet')

        self.status_label = QLabel('Status: WAITING')
        self.status_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.addLayout(self.top_row)
        layout.addWidget(self.avatar_label)
        layout.addWidget(self.name_label)
        layout.addWidget(self.cards_label)

        chips_row = QHBoxLayout()
        chips_row.addWidget(self.stack_chip)
        chips_row.addWidget(self.bet_chip)
        layout.addLayout(chips_row)

        layout.addWidget(self.status_label)
        self.setLayout(layout)

    def _set_role_badges(self, is_dealer: bool, blind_role: str | None):
        self.dealer_badge.setVisible(is_dealer)
        if blind_role:
            self.role_badge.setText(blind_role)
            self.role_badge.show()
        else:
            self.role_badge.hide()

    def render_waiting(self, seat_num: int):
        self.name_label.setText(f'Player {seat_num}')
        self.cards_label.setText('🂠  🂠')
        self.stack_chip.setText('Stack  --')
        self.bet_chip.setText('Live Bet  --')
        self.status_label.setText('Status: WAITING')
        self._set_role_badges(False, None)
        self.setProperty('seatState', 'waiting')
        self.style().unpolish(self)
        self.style().polish(self)

    def render_player(self, player, is_active: bool = False, is_dealer: bool = False, blind_role=None, reveal_cards: bool = False):
        status = []
        if player.folded:
            status.append('FOLDED')
        if player.all_in:
            status.append('ALL-IN')
        if not status:
            status.append('ACTIVE')
        if is_active:
            status.insert(0, 'TURN')

        self.name_label.setText(player.name)
        if reveal_cards and player.hole_cards:
            self.cards_label.setText('  '.join(str(card) for card in player.hole_cards))
        else:
            self.cards_label.setText('🂠  🂠')
        self.stack_chip.setText(f'Stack  {player.stack}')
        self.bet_chip.setText(f'Live Bet  {player.current_bet}')
        self.status_label.setText(f"Status: {' | '.join(status)}")
        self._set_role_badges(is_dealer, blind_role)

        if player.folded:
            state = 'folded'
        elif is_active:
            state = 'active'
        else:
            state = 'normal'
        self.setProperty('seatState', state)
        self.style().unpolish(self)
        self.style().polish(self)


class TableView(QWidget):
    def __init__(self):
        super().__init__()

        self.header_label = QLabel('Poker Table')
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.setStyleSheet('font-size: 24px; font-weight: 800; color: #f8fafc;')

        self.subheader_label = QLabel('Spectator View — hole cards hidden until showdown')
        self.subheader_label.setAlignment(Qt.AlignCenter)
        self.subheader_label.setStyleSheet('font-size: 12px; color: #94a3b8;')

        self.street_label = QLabel('Street: --')
        self.pot_label = QLabel('Pot: 0')
        self.phase_label = QLabel('Phase: IDLE')
        self.board_title = QLabel('Community Cards')
        self.board_title.setAlignment(Qt.AlignCenter)
        self.board_title.setStyleSheet('font-size: 14px; font-weight: 700; color: #dbeafe;')

        info_row = QHBoxLayout()
        info_row.setSpacing(12)
        for widget in (self.street_label, self.pot_label, self.phase_label):
            widget.setAlignment(Qt.AlignCenter)
            widget.setObjectName('tableInfoBadge')
            info_row.addWidget(widget)

        self.board_slots = []
        board_row = QHBoxLayout()
        board_row.setSpacing(8)
        for _ in range(5):
            slot = QLabel('--')
            slot.setAlignment(Qt.AlignCenter)
            slot.setObjectName('boardCard')
            slot.setMinimumSize(58, 84)
            slot.setStyleSheet(card_style('--'))
            self.board_slots.append(slot)
            board_row.addWidget(slot)

        self.pot_chip = QLabel('Main Pot\n0')
        self.pot_chip.setAlignment(Qt.AlignCenter)
        self.pot_chip.setObjectName('potChip')

        self.table_surface = QFrame()
        self.table_surface.setObjectName('tableSurface')
        table_layout = QGridLayout()
        table_layout.setContentsMargins(28, 24, 28, 24)
        table_layout.setHorizontalSpacing(30)
        table_layout.setVerticalSpacing(26)

        self.seats = [PlayerSeat(f'Player {i + 1}') for i in range(4)]
        table_layout.addWidget(self.seats[0], 0, 0)
        table_layout.addWidget(self.seats[1], 0, 2)

        center = QFrame()
        center.setObjectName('boardPanel')
        center_layout = QVBoxLayout()
        center_layout.setSpacing(12)
        center_layout.addWidget(self.board_title)
        center_layout.addLayout(board_row)
        center_layout.addWidget(self.pot_chip, alignment=Qt.AlignCenter)
        center.setLayout(center_layout)
        table_layout.addWidget(center, 1, 1)

        table_layout.addWidget(self.seats[2], 2, 0)
        table_layout.addWidget(self.seats[3], 2, 2)
        table_layout.setColumnStretch(1, 1)
        table_layout.setRowStretch(1, 1)
        self.table_surface.setLayout(table_layout)

        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.addWidget(self.header_label)
        layout.addWidget(self.subheader_label)
        layout.addLayout(info_row)
        layout.addWidget(self.table_surface)
        self.setLayout(layout)

        self.setStyleSheet(
            '''
            QWidget { background: #0b1220; color: #edf2f7; }
            #tableSurface {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #166534, stop:1 #14532d);
                border: 3px solid #8b5a2b;
                border-radius: 42px;
                padding: 14px;
            }
            #tableInfoBadge {
                background: #081226;
                border: 1px solid #1e3a5f;
                border-radius: 10px;
                padding: 8px 10px;
                font-size: 15px;
                font-weight: 700;
                color: #eff6ff;
            }
            #boardPanel {
                background: transparent;
            }
            #boardCard {
                background: #f8fafc;
                border-radius: 10px;
                font-size: 18px;
                font-weight: 800;
            }
            #seatCard {
                background: rgba(15, 23, 42, 0.88);
                border: 2px solid #334155;
                border-radius: 18px;
                min-width: 215px;
                min-height: 190px;
                padding: 12px;
            }
            #seatCard[seatState="active"] {
                border: 2px solid #f6e05e;
                background: rgba(82, 63, 15, 0.72);
            }
            #seatCard[seatState="folded"] {
                border: 2px solid #7f1d1d;
                background: rgba(69, 10, 10, 0.75);
            }
            #avatarLabel {
                color: #60a5fa;
                font-size: 28px;
                font-weight: 900;
            }
            #holeCardsLabel {
                color: #e2e8f0;
                font-size: 24px;
                font-weight: 700;
            }
            #chipBadge, #chipBadgeBet {
                border-radius: 14px;
                padding: 8px 10px;
                font-size: 12px;
                font-weight: 800;
                min-height: 30px;
            }
            #chipBadge {
                background: #1d4ed8;
                border: 1px solid #60a5fa;
            }
            #chipBadgeBet {
                background: #92400e;
                border: 1px solid #f59e0b;
            }
            #dealerBadge {
                background: #f8fafc;
                color: #111827;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 900;
                min-width: 24px;
                min-height: 24px;
                max-width: 24px;
                max-height: 24px;
            }
            #roleBadge {
                background: #0f172a;
                color: #f8fafc;
                border: 1px solid #475569;
                border-radius: 10px;
                font-size: 11px;
                font-weight: 900;
                padding: 3px 8px;
            }
            #potChip {
                background: #7c2d12;
                color: #fff7ed;
                border: 2px solid #fdba74;
                border-radius: 28px;
                padding: 10px 18px;
                font-size: 16px;
                font-weight: 900;
                min-width: 120px;
            }
            '''
        )

    def render_state(self, state, phase: str | None = None):
        phase_normalized = (phase or "idle").lower()
        reveal_cards = bool(state and getattr(state, "reveal_all_hole_cards", False)) or phase_normalized == "finished"
        current_phase = phase_normalized.upper()
        self.phase_label.setText(f'Phase: {current_phase}')

        if state is None:
            self.subheader_label.setText('Spectator View — hole cards hidden until showdown')
            self.street_label.setText('Street: --')
            self.pot_label.setText('Pot: 0')
            self.pot_chip.setText('Main Pot\n0')
            for slot in self.board_slots:
                slot.setText('--')
                slot.setStyleSheet(card_style('--'))
            for i, seat in enumerate(self.seats, start=1):
                seat.render_waiting(i)
            return

        if reveal_cards:
            self.subheader_label.setText('Hand complete — all player hole cards revealed')
        else:
            self.subheader_label.setText('Spectator View — hole cards hidden until showdown')

        self.street_label.setText(f'Street: {state.street.upper()}')
        self.pot_label.setText(f'Pot: {state.pot}')
        self.pot_chip.setText(f'Main Pot\n{state.pot}')

        board_cards = [str(c) for c in state.community_cards]
        while len(board_cards) < 5:
            board_cards.append('--')
        for slot, card_text in zip(self.board_slots, board_cards):
            slot.setText(card_text)
            slot.setStyleSheet(card_style(card_text))

        active_index = getattr(state, 'current_player_index', None)
        dealer_index = getattr(state, 'dealer_index', None)
        sb_index = ((dealer_index + 1) % len(state.players)) if dealer_index is not None else None
        bb_index = ((dealer_index + 2) % len(state.players)) if dealer_index is not None else None
        for i, player in enumerate(state.players):
            blind_role = None
            if i == sb_index:
                blind_role = 'SB'
            elif i == bb_index:
                blind_role = 'BB'
            self.seats[i].render_player(
                player,
                is_active=(i == active_index),
                is_dealer=(i == dealer_index),
                blind_role=blind_role,
                reveal_cards=reveal_cards,
            )
