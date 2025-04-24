import pymysql


class DatabaseManager:
    def __init__(self):
        self.connection = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='',
            database='documents',
            port=3306,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    def execute_query(self, query, params=None, fetch_one=False):
        with self.connection.cursor() as cursor:
            cursor.execute(query, params or ())
            if fetch_one:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
            self.connection.commit()
            return result

    def close(self):
        self.connection.close()
