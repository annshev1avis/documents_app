from PyQt6 import QtWidgets

from ui_files.client_documents_list import Ui_DocumentsList
import utilities


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


class DocumentsListScreen(
    QtWidgets.QWidget,
    Ui_DocumentsList,
    utilities.ListsMixin,
):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.setupUi(self)

        self.load_list(
            self.documents_list,
            self.parent.db.get_client_documents_short_info(self.parent.user_id),
            ""
        )


