import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.login_dialog import LoginDialog
from data.auth import LocalAuthStore


def main():
    app = QApplication(sys.argv)
    auth_store = LocalAuthStore()

    login = LoginDialog()
    if login.exec_() != login.Accepted or not login.user_record:
        sys.exit(0)

    window = MainWindow(user_record=login.user_record, auth_store=auth_store)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
