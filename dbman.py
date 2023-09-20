import sqlite3

class SQLiteManager:
    """ # Notes:
    ## Sqlite3 Data types:
    NULL: Represents a null value.
    INTEGER: Represents a whole number (signed integer).
    REAL: Represents a floating-point number.
    TEXT: Represents a text string.
    BLOB: Represents binary data (e.g., images, documents).
    NUMERIC: Represents a numeric value, which can be an integer, real, or text in a specified format. """
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None

    def connect(self):
        """
        ## Establishes a connection to the SQLite database specified during class initialization.
        
        #### Example Usage:
        db_manager = SQLiteManager("my_database") # db filename: my_database.db
        db_manager.connect_to_db()
        """
        self.conn = sqlite3.connect(self.db_name + ".db")
        self.conn.execute("PRAGMA foreign_keys = 1")

    def add_table(self, table_name, columns):
        """
        ## Creates a new table named 'table_name' in the database with the specified list of 'columns'.
        
        #### Example Usage:
        db_manager.add_table("users", ["username TEXT", "email TEXT"])
        """
        with self.conn:
            columns_str = ', '.join(columns)
            query = f"CREATE TABLE IF NOT EXISTS {table_name} (ID INTEGER PRIMARY KEY AUTOINCREMENT, {columns_str})"
            self.conn.execute(query)

    def clear_table(self, table_name):
        """
        ## Removes all records from the specified 'table_name', effectively clearing its contents while keeping its structure intact.
        
        #### Example Usage:
        db_manager.clear_table("users")
        """
        with self.conn:
            query = f"DELETE FROM {table_name}"
            self.conn.execute(query)

    def delete_table(self, table_name):
        """
        ## Deletes the specified 'table_name' from the database, including its structure and contents.
        
        #### Example Usage:
        db_manager.delete_table("users")
        """
        with self.conn:
            query = f"DROP TABLE IF EXISTS {table_name}"
            self.conn.execute(query)

    def add_to_table(self, table_name):
        """
        ## Adds a new empty record to the specified 'table_name'.
        
        #### Example Usage:
        db_manager.add_to_table("users")
        """
        with self.conn:
            query = f"INSERT INTO {table_name} DEFAULT VALUES"
            self.conn.execute(query)

    def insert_to_table(self, table_name, values):
        """
        ## Inserts a new record with the provided 'values' into the specified 'table_name'.
        
        #### Example Usage:
        user_data = (1, "john_doe", "john@example.com")
        db_manager.insert_to_table("users", user_data)
        """
        with self.conn:
            placeholders = ', '.join(['?' for _ in values[1:]])  # Exclude the first value (id)
            query = f"INSERT INTO {table_name} (username, email) VALUES ({placeholders})"
            self.conn.execute(query, values[1:])  # Exclude the first value (id)

    def delete_from_table(self, table_name, condition):
        """
        ## Deletes records from the specified 'table_name' that match the given 'condition'.
        
        #### Example Usage:
        db_manager.delete_from_table("users", "id = 1")
        """
        with self.conn:
            query = f"DELETE FROM {table_name} WHERE {condition}"
            self.conn.execute(query)

    def get_from_table(self, table_name, columns="*", condition=None):
        """
        ## Retrieves records from the specified 'table_name' based on the provided 'condition'.
        If no 'condition' is provided, retrieves all records. You can specify the desired 'columns' to retrieve as well.
        
        #### Example Usage:
        all_records = db_manager.get_from_table("users")
        specific_records = db_manager.get_from_table("users", condition="username='john_doe'")
        """
        query = f"SELECT {columns} FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"

        cursor = self.conn.execute(query)
        return cursor.fetchall()

    def get_record_from_table(self, table_name, condition):
        """
        ## Retrieves a single record from the specified 'table_name' based on the provided 'condition'.
        
        #### Example Usage:
        specific_record = db_manager.get_record_from_table("users", "id = 1")
        """
        query = f"SELECT * FROM {table_name} WHERE {condition}"
        cursor = self.conn.execute(query)
        return cursor.fetchone()

    def close_connection(self):
        """
        ## Closes the database connection, releasing associated resources.
        
        #### Example Usage:
        db_manager.close_connection()
        """
        if self.conn:
            self.conn.close()

db = SQLiteManager("users")
db.connect()
db.get_record_from_table("users", "username = 'parsasssSS'")
