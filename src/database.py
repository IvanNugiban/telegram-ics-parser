
import sqlite3

class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = sqlite3.connect('database.db')
        self.cursor = self.connection.cursor()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                file_path TEXT NOT NULL
        )
        ''')

        self.connection.commit()

    def add_file(self, username, file_path):
        self.cursor.execute('''
            INSERT INTO user_files (username, file_path)
            VALUES (?, ?)
        ''', (username, file_path))

        self.connection.commit()

    def get_files(self):
        self.cursor.execute('''
            SELECT * FROM user_files
        ''')

        return [{'name': row[1], 'file': row[2]} for row in self.cursor.fetchall()]

    def close(self):
        self.connection.close()