from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit


class ActionLogPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.title = QLabel('Action Log')
        self.title.setStyleSheet('font-size: 14px; font-weight: 800; color: #e2e8f0;')
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet(
            '''
            QTextEdit {
                background: #020617;
                color: #e2e8f0;
                border: 1px solid #1d4ed8;
                border-radius: 8px;
                padding: 6px;
            }
            '''
        )

        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addWidget(self.log_box)
        self.setLayout(layout)

    def render_log(self, action_log):
        self.log_box.clear()
        self.log_box.setPlainText('\n'.join(action_log))
