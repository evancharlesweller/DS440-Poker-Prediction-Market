from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
)

from data.auth import LocalAuthStore


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Login - Poker Prediction Market')
        self.setModal(True)
        self.resize(420, 240)

        self.auth = LocalAuthStore()
        self.user_record = None

        self.title_label = QLabel('Local Demo Login')
        self.title_label.setStyleSheet('font-size: 20px; font-weight: 700; color: #e2e8f0;')
        self.info_label = QLabel(
            'Use the built-in demo account (demo / demo) or create a new local user.'
        )
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet('color: #e2e8f0;')

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Username')
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Password')
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_btn = QPushButton('Login')
        self.register_btn = QPushButton('Register')
        self.cancel_btn = QPushButton('Cancel')

        btn_row = QHBoxLayout()
        btn_row.addWidget(self.login_btn)
        btn_row.addWidget(self.register_btn)
        btn_row.addWidget(self.cancel_btn)

        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.info_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addLayout(btn_row)
        self.setLayout(layout)

        self.login_btn.clicked.connect(self._handle_login)
        self.register_btn.clicked.connect(self._handle_register)
        self.cancel_btn.clicked.connect(self.reject)

        self.setStyleSheet(
            '''
            QDialog { background: #12161f; color: white; }
            QLineEdit {
                background: #1d2330;
                border: 1px solid #394355;
                border-radius: 8px;
                padding: 10px;
                color: #edf2f7;
            }
            QPushButton {
                background: #2b6cb0;
                color: white;
                border: none;
                padding: 10px 14px;
                border-radius: 8px;
                font-weight: 600;
            }
            QPushButton:hover { background: #3182ce; }
            '''
        )



    def _credentials(self):
        return self.username_input.text().strip(), self.password_input.text()

    def _handle_login(self):
        username, password = self._credentials()
        user = self.auth.authenticate(username, password)

        if not user:
            show_warning(self, "Login Failed", "Invalid username or password.")
            return
        self.user_record = user
        self.accept()

    def _handle_register(self):
        username, password = self._credentials()
        try:
            user = self.auth.register_user(username, password)
        except ValueError as exc:
            show_warning(self, 'Registration Failed', str(exc))
            return
        self.user_record = user
        show_info(self, 'Registration Complete', f"Created local user '{username}'. You are now logged in.")
        self.accept()

def show_warning(parent, title, text):
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle(title)
    msg.setText(text)

    msg.setStyleSheet("""
        QMessageBox {
            background-color: #12161f;
        }
        QLabel {
            color: #e2e8f0;
            font-size: 14px;
        }
        QPushButton {
            color: #e2e8f0;
            background-color: #3182ce;
            padding: 5px 12px;
        }
    """)

    msg.exec_()

def show_info(parent, title, text):
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle(title)
    msg.setText(text)

    msg.setStyleSheet("""
        QMessageBox {
            background-color: #12161f;
        }
        QLabel {
            color: #e2e8f0;
            font-size: 14px;
        }
        QPushButton {
            color: #e2e8f0;
            background-color: #3182ce;
            padding: 5px 12px;
        }
    """)

    msg.exec_()