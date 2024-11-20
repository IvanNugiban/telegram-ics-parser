import sqlite3

class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = sqlite3.connect('database.db')
        self.cursor = self.connection.cursor()

    def create_chat_table(self, chat_id):
        table_name = f"chat_files_{chat_id}"
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS "{table_name}" (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                file_path TEXT NOT NULL
            )
        ''')
        self.connection.commit()

    def add_file(self, chat_id, name, file_path):
        table_name = f"chat_files_{chat_id}"
        cursor = self.connection.cursor()
        cursor.execute(f'''
            INSERT INTO "{table_name}" (name, file_path)
            VALUES (?, ?)
        ''', (name, file_path))
        self.connection.commit()

    def get_row(self, chat_id, name):
        self.create_chat_table(chat_id)
        table_name = f"chat_files_{chat_id}"
        self.cursor.execute(f'''
            SELECT * FROM "{table_name}" WHERE name = ?
        ''', (name,))
        return self.cursor.fetchone()

    def get_files(self, chat_id):
        self.create_chat_table(chat_id)
        table_name = f"chat_files_{chat_id}"
        self.cursor.execute(f'''
            SELECT * FROM "{table_name}"
        ''')
        return [{'name': row[1], 'file': row[2]} for row in self.cursor.fetchall()]

    def remove_row(self, chat_id, name):
        table_name = f"chat_files_{chat_id}"
        self.cursor.execute(f'''
            DELETE FROM "{table_name}" WHERE name = ?
        ''', (name,))
        self.connection.commit()

    def create_schedule_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                chat_id INTEGER PRIMARY KEY NOT NULL,
                date TEXT NOT NULL,
                days_ahead INTEGER NOT NULL
            )
        ''')
        self.connection.commit()

    def add_schedule(self, chat_id, date, days_ahead):
        self.cursor.execute('''
            INSERT OR REPLACE INTO schedules (chat_id, date, days_ahead)
            VALUES (?, ?, ?)
        ''', (chat_id, date, days_ahead))
        self.connection.commit()

    def remove_schedule(self, chat_id):
        self.cursor.execute('''
            DELETE FROM schedules WHERE chat_id = ?
        ''', (chat_id,))
        self.connection.commit()

    def get_schedules(self):
        self.cursor.execute('''
            SELECT * FROM schedules
        ''')
        return self.cursor.fetchall()

    def get_schedule(self, chat_id):
        self.cursor.execute('''
            SELECT * FROM schedules WHERE chat_id = ?
        ''', (chat_id,))
        return self.cursor.fetchone

    def close(self):
        self.connection.close()