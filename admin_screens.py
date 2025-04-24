import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QTextEdit,
                             QComboBox, QStackedWidget, QFileDialog, QMessageBox, QHeaderView, QTabWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

from database import DatabaseManager


class AdminDashboard(QWidget):
    init_request_details_window = pyqtSignal(int)
    init_add_user_window = pyqtSignal()

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.db = DatabaseManager()
        self.init_ui()
        self.load_all_requests()
        self.load_users()

    def init_ui(self):
        layout = QVBoxLayout()

        # Заголовок
        self.title_label = QLabel(f'Панель администратора')
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        # Вкладки
        self.tabs = QTabWidget()

        # Вкладка заявок
        self.requests_tab = QWidget()
        requests_tab_layout = QVBoxLayout()

        self.requests_table = QTableWidget()
        self.requests_table.setColumnCount(8)
        self.requests_table.setHorizontalHeaderLabels(
            ['ID', 'Название', 'Тип', 'Дата', 'Клиент', 'Оператор', 'Статус', 'Приоритет'])
        self.requests_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.requests_table.doubleClicked.connect(self.show_request_details)

        # Фильтры
        filters_layout = QHBoxLayout()

        self.status_filter = QComboBox()
        self.status_filter.addItem('Все статусы', 0)
        statuses = self.db.execute_query("SELECT id, name FROM statuses")
        for status in statuses:
            self.status_filter.addItem(str(status['name']), status['id'])

        self.type_filter = QComboBox()
        self.type_filter.addItem('Все типы', 0)
        types = self.db.execute_query("SELECT id, name FROM types")
        for type_ in types:
            self.type_filter.addItem(type_['name'], type_['id'])

        self.min_price_input = QLineEdit()
        self.min_price_input.setPlaceholderText('Мин. сумма')

        filter_button = QPushButton('Фильтровать')
        filter_button.clicked.connect(self.apply_filters)

        filters_layout.addWidget(QLabel('Статус:'))
        filters_layout.addWidget(self.status_filter)
        filters_layout.addWidget(QLabel('Тип:'))
        filters_layout.addWidget(self.type_filter)
        filters_layout.addWidget(self.min_price_input)
        filters_layout.addWidget(filter_button)

        requests_tab_layout.addLayout(filters_layout)
        requests_tab_layout.addWidget(self.requests_table)

        # кнопка обновления
        self.update_requests_button = QPushButton("Обновить")
        self.update_requests_button.clicked.connect(self.load_all_requests)
        requests_tab_layout.addWidget(
            self.update_requests_button
        )

        self.requests_tab.setLayout(requests_tab_layout)

        # Вкладка пользователей
        self.users_tab = QWidget()
        users_tab_layout = QVBoxLayout()

        self.users_table = QTableWidget()
        self.users_table.setColumnCount(3)
        self.users_table.setHorizontalHeaderLabels(['ID', 'Имя пользователя', 'Роль'])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.add_user_button = QPushButton('Добавить пользователя')
        self.add_user_button.clicked.connect(self.show_add_user_form)

        users_tab_layout.addWidget(self.users_table)
        users_tab_layout.addWidget(self.add_user_button)
        self.users_tab.setLayout(users_tab_layout)

        self.tabs.addTab(self.requests_tab, 'Заявки')
        self.tabs.addTab(self.users_tab, 'Пользователи')

        layout.addWidget(self.title_label)
        layout.addWidget(self.tabs)

        self.setLayout(layout)

    def load_all_requests(self):
        query = """
        SELECT d.id, d.name, t.name as type, d.date_signed, 
               c.username as client, o.username as operator, 
               s.name as status, d.priority_level 
        FROM documents d 
        JOIN types t ON d.type_id = t.id 
        JOIN statuses s ON d.status_id = s.id 
        JOIN users c ON d.client_id = c.id 
        JOIN users o ON d.operator_id = o.id
        """
        requests = self.db.execute_query(query)

        self.requests_table.setRowCount(len(requests))
        for row, request in enumerate(requests):
            self.requests_table.setItem(row, 0, QTableWidgetItem(str(request['id'])))
            self.requests_table.setItem(row, 1, QTableWidgetItem(request['name']))
            self.requests_table.setItem(row, 2, QTableWidgetItem(request['type']))
            self.requests_table.setItem(row, 3, QTableWidgetItem(str(request['date_signed'])))
            self.requests_table.setItem(row, 4, QTableWidgetItem(request['client']))
            self.requests_table.setItem(row, 5, QTableWidgetItem(request['operator']))
            self.requests_table.setItem(row, 6, QTableWidgetItem(str(request['status'])))
            self.requests_table.setItem(row, 7, QTableWidgetItem(request['priority_level']))

    def load_users(self):
        query = """
        SELECT u.id, u.username, r.name as role 
        FROM users u 
        JOIN roles r ON u.role_id = r.id
        """
        users = self.db.execute_query(query)

        self.users_table.setRowCount(len(users))
        for row, user in enumerate(users):
            self.users_table.setItem(row, 0, QTableWidgetItem(str(user['id'])))
            self.users_table.setItem(row, 1, QTableWidgetItem(user['username']))
            self.users_table.setItem(row, 2, QTableWidgetItem(str(user['role'])))

    def apply_filters(self):
        status_id = self.status_filter.currentData()
        type_id = self.type_filter.currentData()
        min_price = self.min_price_input.text()

        query = """
        SELECT d.id, d.name, t.name as type, d.date_signed, 
               c.username as client, o.username as operator, 
               s.name as status, d.priority_level 
        FROM documents d 
        JOIN types t ON d.type_id = t.id 
        JOIN statuses s ON d.status_id = s.id 
        JOIN users c ON d.client_id = c.id 
        JOIN users o ON d.operator_id = o.id
        WHERE 1=1
        """

        params = []

        if status_id != 0:
            query += " AND s.id = %s"
            params.append(status_id)

        if type_id != 0:
            query += " AND t.id = %s"
            params.append(type_id)

        if min_price:
            query += " AND d.price >= %s"
            params.append(int(min_price))

        requests = self.db.execute_query(query, params)

        self.requests_table.setRowCount(len(requests))
        for row, request in enumerate(requests):
            self.requests_table.setItem(row, 0, QTableWidgetItem(str(request['id'])))
            self.requests_table.setItem(row, 1, QTableWidgetItem(request['name']))
            self.requests_table.setItem(row, 2, QTableWidgetItem(request['type']))
            self.requests_table.setItem(row, 3, QTableWidgetItem(str(request['date_signed'])))
            self.requests_table.setItem(row, 4, QTableWidgetItem(request['client']))
            self.requests_table.setItem(row, 5, QTableWidgetItem(request['operator']))
            self.requests_table.setItem(row, 6, QTableWidgetItem(str(request['status'])))
            self.requests_table.setItem(row, 7, QTableWidgetItem(request['priority_level']))

    def show_request_details(self, index):
        request_id = int(self.requests_table.item(index.row(), 0).text())
        self.init_request_details_window.emit(request_id)

    def show_add_user_form(self):
        self.init_add_user_window.emit()


class AddUserWindow(QWidget):
    load_users_in_admin_dashboard = pyqtSignal()

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.username_label = QLabel('Имя пользователя:')
        self.username_input = QLineEdit()

        self.password_label = QLabel('Пароль:')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.role_label = QLabel('Роль:')
        self.role_combo = QComboBox()
        roles = self.db.execute_query("SELECT id, name FROM roles")
        for role in roles:
            self.role_combo.addItem(str(role['name']), role['id'])

        buttons_layout = QHBoxLayout()
        self.submit_button = QPushButton('Добавить')
        self.submit_button.clicked.connect(self.add_user)
        self.cancel_button = QPushButton('Отмена')
        self.cancel_button.clicked.connect(self.close)

        buttons_layout.addWidget(self.submit_button)
        buttons_layout.addWidget(self.cancel_button)

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.role_label)
        layout.addWidget(self.role_combo)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def add_user(self):
        username = self.username_input.text()
        password = self.password_input.text()
        role_id = self.role_combo.currentData()

        if not username or not password:
            QMessageBox.warning(self, 'Ошибка', 'Заполните все поля')
            return

        try:
            existing_user = self.db.execute_query(
                "SELECT id FROM users WHERE username = %s",
                (username,),
                fetch_one=True
            )

            if existing_user:
                QMessageBox.warning(self, 'Ошибка', 'Пользователь с таким именем уже существует')
                return

            # Добавляем нового пользователя
            query = "INSERT INTO users (username, password, role_id) VALUES (%s, %s, %s)"
            self.db.execute_query(query, (username, password, role_id))

            QMessageBox.information(self, 'Успех', 'Пользователь добавлен')
            self.close()
            self.load_users_in_admin_dashboard.emit()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при добавлении пользователя: {str(e)}')
