import pymysql


class DatabaseManager:
    def __init__(self, host, user, password, database):
        self.database = database
        self.connection = pymysql.connect(
            host=host, user=user, passwd=password, db=database, charset="utf8"
        )

    def __del__(self):
        self.connection.close()
        self.connection.cursor().close()

    def _execute(self, statement, values=None):
        with self.connection.cursor() as cursor:
            use_database = f"USE {self.database}"
            cursor.execute(use_database)
            cursor.execute(statement, values)
            cursor.connection.commit()
            return cursor

    def add(self, table_name, data):
        column_names = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        column_values = tuple(data.values())
        insert_sql = f"""
            INSERT INTO {table_name} ({column_names})
            VALUES ({placeholders});
        """
        self._execute(insert_sql, column_values)

    def delete(self, table_name, criteria):
        placeholders = [f"{column} = %s" for column in criteria.keys()]
        delete_criteria = " AND ".join(placeholders)
        delete_sql = f"""
            DELETE FROM {table_name}
            WHERE {delete_criteria}
        """
        self._execute(delete_sql, tuple(criteria.values()))

    def select(self, table_name, criteria=None, order_by=None):
        criteria = criteria or {}
        query = f"SELECT * FROM {table_name}"

        if criteria:
            placeholders = [f"{column} = %s" for column in criteria.keys()]
            select_criteria = " AND ".join(placeholders)
            query += f" WHERE {select_criteria}"

        if order_by:
            query += f" ORDER BY {order_by}"

        return self._execute(
            query,
            tuple(criteria.values()),
        )
