import pymysql


class Database:
    def __init__(self):
        self.con = pymysql.connect(
            host="127.0.0.1",
            user="root",
            password="",
            database="documents"
        )
        self.cur = self.con.cursor()

    def get_client_documents_short_info(self, client_id):
        self.cur.execute(
            "select id, name, type, price, status "
            "from document_with_related_data "
            "where client_id = % s",
            (client_id, )
        )
        return self.cur.fetchall()