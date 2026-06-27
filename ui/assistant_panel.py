from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QLineEdit, QPushButton
)


class AssistantPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._service = None

        self.title = QLabel("Betting Assistant")
        self.title.setStyleSheet("font-size: 14px; font-weight: 800; color: #e2e8f0;")
        self.subtitle = QLabel(
            "Ask about the table, card odds, the safest bet, or the biggest payout available right now."
        )
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet("color: #93c5fd;")

        self.history = QTextEdit()
        self.history.setReadOnly(True)
        self.history.setStyleSheet(
            """
            QTextEdit {
                background: #020617;
                color: #e2e8f0;
                border: 1px solid #1d4ed8;
                border-radius: 8px;
                padding: 6px;
            }
            """
        )

        self.input = QLineEdit()
        self.input.setPlaceholderText("Ask: What are the chances there is a 4 of diamonds?")
        self.input.returnPressed.connect(self.submit_query)
        self.input.setStyleSheet(
            "QLineEdit { background: #0f172a; color: #f8fafc; border: 1px solid #475569; border-radius: 8px; padding: 8px; }"
        )

        self.send_btn = QPushButton("Ask")
        self.send_btn.clicked.connect(self.submit_query)
        self.best_bet_btn = QPushButton("Best Bets")
        self.best_bet_btn.clicked.connect(lambda: self.ask_preset("What is the best bet right now?"))
        self.highest_payout_btn = QPushButton("Highest Payout")
        self.highest_payout_btn.clicked.connect(lambda: self.ask_preset("What is the highest payout I can get right now?"))
        self.summary_btn = QPushButton("Summarize State")
        self.summary_btn.clicked.connect(lambda: self.ask_preset("Summarize the current game state."))

        for btn in (self.send_btn, self.best_bet_btn, self.highest_payout_btn, self.summary_btn):
            btn.setStyleSheet(
                "QPushButton { background: #2563eb; border: none; border-radius: 8px; padding: 8px; color: white; font-weight: 700; }"
                "QPushButton:hover { background: #3b82f6; }"
            )

        button_row = QHBoxLayout()
        button_row.addWidget(self.best_bet_btn)
        button_row.addWidget(self.highest_payout_btn)
        button_row.addWidget(self.summary_btn)
        button_row.addStretch(1)
        button_row.addWidget(self.send_btn)

        input_row = QHBoxLayout()
        input_row.addWidget(self.input, 1)

        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)
        layout.addWidget(self.history, 1)
        layout.addLayout(button_row)
        layout.addLayout(input_row)
        self.setLayout(layout)

    def set_service(self, service):
        self._service = service

    def append_message(self, speaker: str, text: str):
        self.history.append(f"{speaker}:\n{text}\n")

    def ask_preset(self, prompt: str):
        self.input.setText(prompt)
        self.submit_query()

    def submit_query(self):
        message = self.input.text().strip()
        if not message:
            return
        self.append_message("You", message)
        if self._service is None:
            reply = "Assistant is not connected yet."
        else:
            reply = self._service.answer(message)
        self.append_message("Assistant", reply)
        self.input.clear()
