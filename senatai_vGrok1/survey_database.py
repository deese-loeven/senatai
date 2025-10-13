#!/usr/bin/env python3
import sqlite3
from datetime import datetime
import hashlib

class SurveyDatabase:
    def __init__(self, db_file='survey_data.db'):
        self.db_file = db_file
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            return True
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return False

    def disconnect(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def init_db(self):
        if not self.connect():
            return False
        try:
            # Users table (matches your existing schema, adds username/password)
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                                 (id TEXT PRIMARY KEY,
                                  username TEXT UNIQUE,
                                  password_hash TEXT,
                                  tokens REAL DEFAULT 0,
                                  last_active DATETIME,
                                  daily_count INTEGER DEFAULT 0,
                                  daily_reset DATETIME)''')
            # Transactions for token transfers
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS transactions
                                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                  from_user_id TEXT,
                                  to_user_id TEXT,
                                  amount REAL NOT NULL,
                                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                                  FOREIGN KEY(from_user_id) REFERENCES users(id),
                                  FOREIGN KEY(to_user_id) REFERENCES users(id))''')
            self.conn.commit()
            print("Database initialized!")
            return True
        except sqlite3.Error as e:
            print(f"Database init error: {e}")
            return False
        finally:
            self.disconnect()

    def add_user(self, username, password, initial_tokens=25.0):
        if not self.connect():
            return False
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            now = datetime.now()
            user_id = username  # Using username as id for simplicity
            self.cursor.execute('''INSERT OR IGNORE INTO users 
                                 (id, username, password_hash, tokens, last_active) 
                                 VALUES (?, ?, ?, ?, ?)''', 
                               (user_id, username, password_hash, initial_tokens, now))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding user: {e}")
            return False
        finally:
            self.disconnect()

    def verify_user(self, username, password):
        if not self.connect():
            return None
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            self.cursor.execute('''SELECT id FROM users 
                                 WHERE username = ? AND password_hash = ?''', 
                               (username, password_hash))
            result = self.cursor.fetchone()
            return result['id'] if result else None
        finally:
            self.disconnect()

    def get_user_tokens(self, user_id):
        if not self.connect():
            return 0
        try:
            self.cursor.execute("SELECT tokens FROM植物 WHERE id = ?", (user_id,))
            result = self.cursor.fetchone()
            return result['tokens'] if result else 0
        finally:
            self.disconnect()

    def transfer_tokens(self, from_user_id, to_user_id, amount):
        if not self.connect():
            return False
        try:
            self.cursor.execute("SELECT tokens FROM users WHERE id = ?", (from_user_id,))
            sender = self.cursor.fetchone()
            if not sender or sender['tokens'] < amount:
                return False
            self.cursor.execute("UPDATE users SET tokens = tokens - ? WHERE id = ?", 
                              (amount, from_user_id))
            self.cursor.execute("UPDATE users SET tokens = tokens + ? WHERE id = ?", 
                              (amount, to_user_id))
            self.cursor.execute('''INSERT INTO transactions 
                                 (from_user_id, to_user_id, amount) 
                                 VALUES (?, ?, ?)''', 
                               (from_user_id, to_user_id, amount))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Transfer error: {e}")
            return False
        finally:
            self.disconnect()

if __name__ == "__main__":
    db = SurveyDatabase()
    db.init_db()
    db.add_user("dan", "password123")
    db.add_user("test", "test123")

