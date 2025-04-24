import os
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QTextEdit,
                             QComboBox, QStackedWidget, QFileDialog, QMessageBox, QGroupBox, QListWidget,
                             QListWidgetItem)
from PyQt6.QtCore import Qt, QUrl, QDir
from PyQt6.QtGui import QIcon, QDesktopServices

from database import DatabaseManager
from ui_files.request_details import Ui_RequestDetails


class LoginWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Вход в систему')
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        self.username_label = QLabel('Имя пользователя:')
        self.username_input = QLineEdit()

        self.password_label = QLabel('Пароль:')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton('Войти')
        self.login_button.clicked.connect(self.authenticate)

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def authenticate(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, 'Ошибка', 'Введите имя пользователя и пароль')
            return

        query = (
            "SELECT id, username, role_id FROM users "
            "WHERE username = %s AND password = %s"
        )
        user = self.db.execute_query(query, (username, password), fetch_one=True)

        if user:
            self.main_window.user_id = user['id']
            self.main_window.user_role_id = user['role_id']
            self.main_window.username = user['username']
            self.main_window.initialize_main_interface()
            self.main_window.stack.setCurrentIndex(1)
        else:
            QMessageBox.warning(self, 'Ошибка', 'Неверное имя пользователя или пароль')


class RequestWindow(QWidget, Ui_RequestDetails):
    def __init__(self, main_window, request_id=None):
        super().__init__()
        self.main_window = main_window
        self.db = DatabaseManager()
        self.request_id = request_id
        self.uploaded_files = []

        self.init_ui()

        if request_id:
            self.load_request_data()
            self.load_messages()
            self.load_files()

    def add_field(self, label, field, editable):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label))
        layout.addWidget(field)

        if editable:
            self.edit_info_layout.addLayout(layout)
        else:
            self.nonedit_info_layout.addLayout(layout)

    def init_files_ui(self):
        # Добавляем компоненты для работы с файлами
        self.files_group = QGroupBox("Прикрепленные файлы")
        self.files_layout = QVBoxLayout()

        # Кнопка загрузки файла
        self.upload_button = QPushButton("Загрузить файл")
        self.upload_button.clicked.connect(self.upload_file)

        # Список файлов
        self.files_list = QListWidget()
        self.files_list.itemDoubleClicked.connect(self.open_file)

        # Кнопка удаления файла
        self.delete_file_button = QPushButton("Удалить выбранный файл")
        self.delete_file_button.clicked.connect(self.delete_file)

        self.files_layout.addWidget(self.upload_button)
        self.files_layout.addWidget(self.files_list)
        self.files_layout.addWidget(self.delete_file_button)
        self.files_group.setLayout(self.files_layout)

        # Добавляем группу файлов в основной layout
        self.info_layout.insertWidget(3, self.files_group)

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "Все файлы (*)")
        if file_path:
            try:
                with open(file_path, 'rb') as file:
                    file_data = file.read()
                    file_name = os.path.basename(file_path)

                    # Сохраняем файл в базе данных
                    self.db.execute_query(
                        "INSERT INTO files (document_id, file_name, file_data) VALUES (%s, %s, %s)",
                        (self.request_id, file_name, file_data)
                    )

                    # Обновляем список файлов
                    self.load_files()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить файл: {str(e)}")

    def load_files(self):
        if not self.request_id:
            return

        self.files_list.clear()
        files = self.db.execute_query(
            "SELECT id, file_name FROM files WHERE document_id = %s",
            (self.request_id,)
        )

        for file in files:
            item = QListWidgetItem(file['file_name'])
            item.setData(Qt.ItemDataRole.UserRole, file['id'])
            self.files_list.addItem(item)

    def open_file(self, item):
        file_id = item.data(Qt.ItemDataRole.UserRole)
        file_data = self.db.execute_query(
            "SELECT file_name, file_data FROM files WHERE id = %s",
            (file_id,),
            fetch_one=True
        )

        if file_data:
            # Создаем временный файл
            temp_dir = QDir.tempPath()
            temp_file_path = os.path.join(temp_dir, file_data['file_name'])

            with open(temp_file_path, 'wb') as temp_file:
                temp_file.write(file_data['file_data'])

            # Открываем файл стандартным способом для ОС
            QDesktopServices.openUrl(QUrl.fromLocalFile(temp_file_path))

    def delete_file(self):
        selected_items = self.files_list.selectedItems()
        if not selected_items:
            return

        file_id = selected_items[0].data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(
            self, 'Подтверждение',
            'Вы уверены, что хотите удалить этот файл?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.db.execute_query(
                "DELETE FROM files WHERE id = %s",
                (file_id,)
            )
            self.load_files()

    def init_ui(self):
        self.setupUi(self)

        if self.main_window.user_role_id == 1:
            self.add_client_fields()
        else:
            self.add_admin_fields()

        self.load_comboboxes()
        self.init_files_ui()
        self.save_button.clicked.connect(self.save_request)
        self.send_button.clicked.connect(self.send_message)

    def add_client_fields(self):
        self.status_label = QLabel()
        self.add_field(
            "Текущий статус",
            self.status_label,
            editable=False,
        )

    def add_admin_fields(self):
        self.operator_combobox = QComboBox()
        self.add_field(
            "Работник, ведущий договор",
            self.operator_combobox,
            editable=True,
        )
        self.status_combobox = QComboBox()
        self.add_field(
            "Текущий статус",
            self.status_combobox,
            editable=True,
        )
        self.priority_combobox = QComboBox()
        self.add_field(
            "Приоритет",
            self.priority_combobox,
            editable=True,
        )

    @staticmethod
    def load_combobox(combobox, data):
        for d in data:
            combobox.addItem(d[1], d[0])

    def load_comboboxes(self):
        types = self.db.execute_query("SELECT id, name FROM types")
        self.load_combobox(
            self.type_combobox,
            [list(d.values()) for d in types]
        )

        if self.main_window.user_role_id == 2:
            operators = self.db.execute_query("SELECT id, username FROM users WHERE role_id = 2")
            self.load_combobox(
                self.operator_combobox,
                [list(d.values()) for d in operators]
            )

            statuses = self.db.execute_query("SELECT id, name FROM statuses")
            self.load_combobox(
                self.status_combobox,
                [list(d.values()) for d in statuses]
            )

            data = [(1, "Низкий"), (2, "Средний"), (3, "Высокий")]
            self.load_combobox(self.priority_combobox, data)

    def load_request_data(self):
        query = """
            SELECT d.id, d.name, t.name as type, d.date_signed, d.price, d.comission_percent, 
                   c.id as client_id, c.username as client, o.id as operator_id, o.username as operator, 
                   s.name as status, d.priority_level 
            FROM documents d 
            JOIN types t ON d.type_id = t.id 
            JOIN statuses s ON d.status_id = s.id 
            JOIN users c ON d.client_id = c.id 
            JOIN users o ON d.operator_id = o.id
            WHERE d.id = %s
            """
        request = self.db.execute_query(query, (self.request_id,), fetch_one=True)

        self.id_label.setText(str(request["id"]))
        self.date_label.setText(str(request["date_signed"]))
        self.name_lineedit.setText(request["name"])
        self.price_spinbox.setValue(request["price"])
        self.comission_spinbox.setValue(request["comission_percent"])

        if self.main_window.user_role_id == 1:
            self.status_label.setText(request["status"])
        else:
            operator_index = self.operator_combobox.findData(request["operator_id"])
            if operator_index >= 0:
                self.operator_combobox.setCurrentIndex(operator_index)

            status_index = self.status_combobox.findText(request["status"])
            if status_index >= 0:
                self.status_combobox.setCurrentIndex(status_index)

            self.priority_combobox.setCurrentText(request["priority_level"])

    def load_messages(self):
        messages = self.db.execute_query(
            "SELECT text FROM messages WHERE document_id = %s",
            (self.request_id,)
        )

        self.messages_list.clear()
        self.messages_list.addItems(m["text"] for m in messages)

    def save_request(self):
        data = {
            "operator_id": 2,
            "status_id": 1,
            "priority_level": 2
        }

        if self.request_id:
            existing_data = self.db.execute_query(
                "SELECT * FROM documents WHERE id = %s",
                (self.request_id,),
                fetch_one=True
            )
            data.update(existing_data)

        data.update(
            {
                "name": self.name_lineedit.text(),
                "type_id": self.type_combobox.currentData(),
                "price": self.price_spinbox.value(),
                "commission_percent": self.comission_spinbox.value(),
                "client_id": self.main_window.user_id,
            }
        )

        if self.main_window.user_role_id == 2:
            data.update(
                {
                    "operator_id": self.operator_combobox.currentData(),
                    "status_id": self.status_combobox.currentData(),
                    "priority_level": self.priority_combobox.currentData(),
                }
            )

        if self.request_id:
            self.update_old_request(data)
        else:
            self.save_new_request(data)

    def save_new_request(self, data):
        self.db.execute_query(
            "INSERT INTO documents(name, type_id, price, comission_percent, "
            "client_id, operator_id, status_id, priority_level) VALUES "
            "(%s, %s, %s, %s, %s, %s, %s, %s)",
            (
                data["name"], data["type_id"], data["price"],
                data["commission_percent"], data["client_id"],
                data["operator_id"], data["status_id"],
                data["priority_level"],
            )
        )
        self.close()

    def update_old_request(self, data):
        self.db.execute_query(
            "UPDATE documents SET name = %s, type_id = %s, price = %s, "
            "comission_percent = %s, operator_id = %s, "
            "status_id = %s, priority_level = %s "
            "WHERE id = %s",
            (
                data["name"], data["type_id"], data["price"],
                data["commission_percent"],
                data["operator_id"], data["status_id"],
                data["priority_level"], self.request_id,
            )
        )
        self.close()

    def send_message(self):
        message = self.message_lineedit.text()

        if message:
            self.db.execute_query(
                "insert into messages (text, document_id) values (%s, %s)",
                (message, self.request_id)
            )

        self.message_lineedit.clear()
        self.load_messages()
