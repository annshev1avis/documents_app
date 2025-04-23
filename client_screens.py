import sys

from PyQt6 import QtWidgets

import database
from ui_files.client_documents_list import Ui_DocumentsList


class ClientMainWindow(QtWidgets.QMainWindow):
    def __init__(self, db, user_id):
        super().__init__()
        self.db = db
        self.user_id = user_id

        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)
        self.init_documents_list_screen()

    def init_documents_list_screen(self):
        self.documents_list_screen = DocumentsListScreen(self)
        self.stack.addWidget(self.documents_list_screen)

    def go_to_single_doc_screen(self, doc_id=None):
        pass


class DocumentsListScreen(QtWidgets.QWidget, Ui_DocumentsList):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.setupUi(self)

        # обработка кнопок
        self.create_button.clicked.connect()

        # загрузка данных
        self.load_list()

    def make_card(self, data):
        card = QtWidgets.QWidget()
        card.data = data
        layout = QtWidgets.QVBoxLayout()
        card.setLayout(layout)

        layout.addWidget(QtWidgets.QLabel(card.data["name"]))
        layout.addWidget(QtWidgets.QLabel(f"Тип: {card.data['name']}"))
        layout.addWidget(QtWidgets.QLabel(f"Цена: {card.data['price']}"))
        layout.addWidget(QtWidgets.QLabel(f"Текущий статус: {card.data['status']}"))

        return card

    def load_list(self):
        self.documents_list.clear()

        docs = self.parent.db.get_client_documents_short_info(
            self.parent.user_id
        )
        for doc in docs:
            list_item = QtWidgets.QListWidgetItem()
            card = self.make_card(doc)

            list_item.setSizeHint(card.sizeHint())
            self.documents_list.addItem(list_item)
            self.documents_list.setWidgetItem(list_item, card)

    def view_doc(self):
        pass


class SingleDocumentScreen(QtWidgets.QWidget):
    pass

if __name__ == "__main__":
    db = database.Database()

    app = QtWidgets.QApplication(sys.argv)
    win = ClientMainWindow(db, 1)
    win.show()
    app.exec()
