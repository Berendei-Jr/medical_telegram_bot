import sqlite3
from datetime import datetime


class DatabaseHandler:
    def __init__(self):
        self.connection = sqlite3.connect('database.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY,
        telegram_id TEXT NOT NULL,
        expiration_time DATETIME NOT NULL,
        current_plan TEXT NOT NULL,
        total_orders INTEGER NOT NULL,
        is_active BOOLEAN NOT NULL
        )
        ''')

    def add_purchase(self, telegram_id, expiration_time, current_plan):
        self.cursor.execute("SELECT * FROM Users WHERE telegram_id = ?", (telegram_id,))
        existing_record = self.cursor.fetchone()

        if existing_record:
            self.cursor.execute("UPDATE Users SET total_orders = total_orders + 1, expiration_time = ?, "
                                "current_plan = ?, "
                                "is_active = true "
                                "WHERE telegram_id = ?", (expiration_time, current_plan, telegram_id,))
        else:
            self.cursor.execute(
                'INSERT INTO Users (telegram_id, expiration_time, current_plan, total_orders, is_active) VALUES (?, ?, ?, ?, ?)',
                (telegram_id, expiration_time, current_plan, 1, True))
        self.connection.commit()

    def check_for_expired_users(self):
        self.cursor.execute("SELECT * FROM Users WHERE is_active=1 AND expiration_time < ?", (datetime.now(),))
        expired_users = self.cursor.fetchall()
        expired_users_ids = [user[1] for user in expired_users]
        for user_id in expired_users_ids:
            self.cursor.execute("UPDATE Users SET is_active = ? WHERE telegram_id IN (?)", (False, user_id))
        self.connection.commit()
        return expired_users_ids

    def __del__(self):
        self.connection.close()
