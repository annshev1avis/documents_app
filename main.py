import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QTextEdit,
                             QComboBox, QStackedWidget, QFileDialog, QMessageBox, QHeaderView, QTabWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

import admin_screens
import database
import client_screens
import common_screens


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_manager = database.DatabaseManager()
        self.user_id = None
        self.user_role_id = None
        self.username = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Система приема и обработки заявок')
        self.setMinimumSize(800, 600)

        self.stack = QStackedWidget()

        # Страница входа
        self.login_page = common_screens.LoginWindow(self)
        self.stack.addWidget(self.login_page)

        # Главная страница (будет заменена на dashboard после входа)
        self.main_page = QWidget()
        self.stack.addWidget(self.main_page)

        self.setCentralWidget(self.stack)

    def initialize_main_interface(self):
        # Удаляем старую главную страницу, если она есть
        if self.stack.count() > 1:
            self.stack.removeWidget(self.main_page)

        # Создаем новую главную страницу в зависимости от роли пользователя
        if self.user_role_id == 1:  # Обычный пользователь
            self.main_page = client_screens.UserDashboard(self)
        else:  # Администратор
            self.main_page = admin_screens.AdminDashboard(self)
            self.main_page.init_request_details_window.connect(self.show_request_details)
            self.main_page.init_add_user_window.connect(self.show_add_user_form)

        self.stack.addWidget(self.main_page)
        self.stack.setCurrentIndex(1)

    def show_request_details(self, request_id):
        self.request_window = common_screens.RequestWindow(self, request_id)
        self.request_window.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.request_window.show()

    def show_new_request_form(self):
        self.new_request_window = common_screens.RequestWindow(self, None)
        self.new_request_window.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.new_request_window.show()

    def show_add_user_form(self):
        self.add_user_window = admin_screens.AddUserWindow(self)
        self.add_user_window.load_users_in_admin_dashboard.connect(
            self.main_page.load_users
        )
        self.add_user_window.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.add_user_window.show()

    def closeEvent(self, event):
        self.db_manager.close()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.user_id = 1
    window.user_role_id = 1
    window.initialize_main_interface()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()