import sys

from PyQt6 import QtWidgets


class Field:
    def __init__(self, label, widget_class, retrieve_method, db_table_name):
        self.label = label
        self.widget = widget_class()
        self.retrieve_method = retrieve_method
        self.db_table_name = db_table_name

    def get_ui(self):
        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(QtWidgets.QLabel(self.label))
        layout.addWidget(self.widget)

        return layout

    def get_value(self):
        return self.retrieve_method(self.widget)


class Form(QtWidgets.QWidget):
    def __init__(self, fields, save_function):
        """
        :param field: list of Field instances
        :param save_function: функция класса db, которая сохраняет запись
        """
        super().__init__()
        self.fields = fields
        self.save_function = save_function

        self.set_ui()

    def set_ui(self):
        layout = QtWidgets.QVBoxLayout()

        for field in self.fields:
            layout.addLayout(field.get_ui())

        self.save_button = QtWidgets.QPushButton("Сохранить")
        self.save_button.clicked.connect(self.get_data)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def get_data(self):
        data = {}
        for field in self.fields:
            if not field.get_value():
                message = QtWidgets.QMessageBox(self)
                message.setWindowTitle("Обнаружены пустые значения")
                message.setText("Заполните все поля")
                message.show()
                return
            data[field.db_table_name] = field.get_value()

        return data

    def save(self):
        object_data = self.get_data()
        if object_data:
            self.save_function(object_data)


class ListsMixin:
    @staticmethod
    def load_list(list_widget, items, card_lines_templates):
        list_widget.clear()

        for card_data in items:
            list_item = QtWidgets.QListWidgetItem
            card = ListsMixin.make_card(
                card_lines_templates,
                card_data,
            )

            list_item.setSizeHint(card.sizeHint())
            list_widget.addItem(list_item)
            list_widget.setItemWidget(list_item, card)


    @staticmethod
    def make_card(lines_templates, card_data):
        card = QtWidgets.QWidget()
        card.data = card_data
        layout = QtWidgets.QVBoxLayout()

        for line in lines_templates:
            layout.addWidget(QtWidgets.QLabel(line.format(**card.data)))

        card.setLayout(layout)
        return card


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = Form(
        [
            Field(
                label="Имя пользователя",
                widget_class=QtWidgets.QLineEdit,
                retrieve_method=QtWidgets.QLineEdit.text,
                db_table_name="username",
            ),
            Field(
                label="Пароль",
                widget_class=QtWidgets.QLineEdit,
                retrieve_method=QtWidgets.QLineEdit.text,
                db_table_name="password",
            )
        ],
        None
    )
    win.show()
    app.exec()
