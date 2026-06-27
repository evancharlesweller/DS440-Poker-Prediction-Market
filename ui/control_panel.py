from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel


class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.session_label = QLabel('Session Controls')
        self.status_label = QLabel('Waiting for New Hand')
        self.new_hand_btn = QPushButton('New Hand')
        self.next_step_btn = QPushButton('Next Step')
        self.run_to_end_btn = QPushButton('Run To End')

        layout = QHBoxLayout()
        layout.addWidget(self.session_label)
        layout.addWidget(self.status_label)
        layout.addStretch(1)
        layout.addWidget(self.new_hand_btn)
        layout.addWidget(self.next_step_btn)
        layout.addWidget(self.run_to_end_btn)

        self.setLayout(layout)
        self.setStyleSheet(
            '''
            QWidget { background: #0b1220; color: #e2e8f0; }
            QPushButton {
                background: #1d4ed8;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 14px;
                font-weight: 700;
            }
            QPushButton:hover { background: #2563eb; }
            QLabel { font-size: 15px; font-weight: 700; }
            '''
        )

    def render_status(self, phase: str, username: str):
        self.status_label.setText(f'User: {username} | Engine: {phase.upper()}')
