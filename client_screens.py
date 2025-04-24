import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QTextEdit,
                             QComboBox, QStackedWidget, QFileDialog, QMessageBox, QHeaderView, QTabWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from database import DatabaseManager


class UserDashboard(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.db = DatabaseManager()
        self.init_ui()
        self.load_user_requests()

    def init_ui(self):
        layout = QVBoxLayout()

        # Заголовок
        self.title_label = QLabel(f'Личный кабинет пользователя')
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        # Таблица заявок
        self.requests_table = QTableWidget()
        self.requests_table.setColumnCount(6)
        self.requests_table.setHorizontalHeaderLabels(['ID', 'Название', 'Тип', 'Дата', 'Статус', 'Приоритет'])
        self.requests_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.requests_table.doubleClicked.connect(self.show_request_details)

        # Кнопки
        buttons_layout = QHBoxLayout()
        self.new_request_button = QPushButton('Новая заявка')
        self.new_request_button.clicked.connect(self.show_new_request_form)
        self.refresh_button = QPushButton('Обновить')
        self.refresh_button.clicked.connect(self.load_user_requests)

        buttons_layout.addWidget(self.new_request_button)
        buttons_layout.addWidget(self.refresh_button)

        layout.addWidget(self.title_label)
        layout.addWidget(self.requests_table)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def load_user_requests(self):
        query = """
            SELECT d.id, d.name, t.name as type, d.date_signed, s.name as status, d.priority_level 
            FROM documents d 
            JOIN types t ON d.type_id = t.id 
            JOIN statuses s ON d.status_id = s.id 
            WHERE d.client_id = %s
            """
        requests = self.db.execute_query(query, (self.main_window.user_id,))

        self.requests_table.setRowCount(len(requests))
        for row, request in enumerate(requests):
            self.requests_table.setItem(row, 0, QTableWidgetItem(str(request['id'])))
            self.requests_table.setItem(row, 1, QTableWidgetItem(request['name']))
            self.requests_table.setItem(row, 2, QTableWidgetItem(request['type']))
            self.requests_table.setItem(row, 3, QTableWidgetItem(str(request['date_signed'])))
            self.requests_table.setItem(row, 4, QTableWidgetItem(str(request['status'])))
            self.requests_table.setItem(row, 5, QTableWidgetItem(request['priority_level']))

    def show_request_details(self, index):
        request_id = int(self.requests_table.item(index.row(), 0).text())
        self.main_window.show_request_details(request_id)

    def show_new_request_form(self):
        self.main_window.show_new_request_form()