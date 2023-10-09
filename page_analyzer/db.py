import psycopg2
import psycopg2.extras


class Database:
    def __init__(self, db_url):
        """
        Initializes the Database object with the provided database URL.

        :param db_url: The URL of the database connection.
        """
        self.db_url = db_url

    def __enter__(self):
        """
        Establishes a connection with the database.
        """
        self.conn = psycopg2.connect(self.db_url)
        self.cursor = self.conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        return self

    def insert(self, table: str, cols, data):
        """
        Inserts a new row into the specified
        table with the provided columns and data.

        :param table: The name of the table.
        :param cols: The list of column names.
        :param data: The data to be inserted into the table.
        :return: The ID of the inserted row.
        """
        self.cursor.execute(
            f'INSERT INTO {table} ({", ".join(str(i) for i in cols)}) '
            f'VALUES ({", ".join("%s" for _ in cols)}) RETURNING id;',
            data if isinstance(data, tuple) else tuple(data)
        )
        return self.cursor.fetchone().get('id')

    def render(self, table: str, item=None, col=None) -> tuple:
        """
        Renders all rows from a table if item is not provided,
        or all rows where item is equal to one in the provided column.

        :param table: The name of the table.
        :param item: The item to filter the rows by (optional).
        :param col: The column to compare the item against (optional).
        :return: A tuple of dictionaries representing the matching rows.
        """
        if item is None or col is None:
            self.cursor.execute(f'SELECT * FROM {table}')
            return self.cursor.fetchall()
        else:
            self.cursor.execute(
                f'SELECT * FROM {table} WHERE {col} = (%s)',
                (item,)
            )
            return self.cursor.fetchall()

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Closes database cursor and connection.
        """
        if self.cursor is not None:
            self.cursor.close()
        if self.conn is not None:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()


def render_data(id, table, col, db_url):
    """
    Retrieves all rows from the specified table where
    the provided item matches the specified column.

    :param id: The id of an item to filter the rows by.
    :param table: The name of the table (urls or urls_checks).
    :param col: The name of the column to compare the item against.
    :return: A list of dictionaries representing the matching rows.
    """
    with Database(db_url) as db:
        data = db.render(table=table, item=id, col=col)
    return data
