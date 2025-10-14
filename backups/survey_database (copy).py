#!/usr/bin/env python3
import sqlite3
import os
from datetime import datetime

class SurveyDatabase:
    def __init__(self, db_file='survey_data.db'):
        """Initialize database connection with specified file"""
        self.db_file = db_file
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Establish connection to the database"""
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            self.cursor = self.conn.cursor()
            return True
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return False
            
    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
    
    def init_db(self):
        """Initialize the database tables"""
        if not self.connect():
            return False
            
        try:
            # Create questions table
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS questions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      question_text TEXT NOT NULL,
                      question_type TEXT NOT NULL,
                      theme TEXT,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
            
            # Create answers table
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS answers
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      question_id INTEGER NOT NULL,
                      answer TEXT NOT NULL,
                      score INTEGER,
                      user_id TEXT NOT NULL,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY(question_id) REFERENCES questions(id),
                      FOREIGN KEY(user_id) REFERENCES users(id))''')
            
            # Create users table
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                     (id TEXT PRIMARY KEY,
                      policap REAL DEFAULT 0,
                      last_active DATETIME,
                      daily_count INTEGER DEFAULT 0,
                      daily_reset DATETIME)''')
                      
            # Create predicted_votes table
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS predicted_votes
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id TEXT NOT NULL,
                      bill_text TEXT NOT NULL,
                      model TEXT NOT NULL,
                      predicted_vote TEXT NOT NULL,
                      confidence INTEGER DEFAULT 50,
                      explanation TEXT,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY(user_id) REFERENCES users(id))''')
                      
            # Create prediction_feedback table
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS prediction_feedback
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      prediction_id INTEGER NOT NULL,
                      username TEXT NOT NULL,
                      agrees INTEGER NOT NULL,
                      timestamp TIMESTAMP NOT NULL,
                      FOREIGN KEY(prediction_id) REFERENCES predicted_votes(id),
                      FOREIGN KEY(username) REFERENCES users(id))''')
            
            self.conn.commit()
            print("Database initialized successfully!")
            return True
            
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
            return False
        finally:
            self.disconnect()
    
    def add_user(self, user_id, initial_policap=25.0):
        """Add a new user to the database"""
        if not self.connect():
            return False
            
        try:
            now = datetime.now()
            self.cursor.execute('''INSERT OR IGNORE INTO users 
                                 (id, policap, last_active, daily_count, daily_reset) 
                                 VALUES (?, ?, ?, ?, ?)''', 
                               (user_id, initial_policap, now, 0, now))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding user: {e}")
            return False
        finally:
            self.disconnect()
    
    def add_question(self, question_text, question_type, theme=None):
        """Add a new question to the database"""
        if not self.connect():
            return False
            
        try:
            now = datetime.now()
            self.cursor.execute('''INSERT INTO questions 
                                 (question_text, question_type, theme, timestamp) 
                                 VALUES (?, ?, ?, ?)''', 
                               (question_text, question_type, theme, now))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding question: {e}")
            return None
        finally:
            self.disconnect()
    
    def add_answer(self, question_id, user_id, answer, score=None):
        """Record a user's answer to a question"""
        if not self.connect():
            return False
            
        try:
            now = datetime.now()
            self.cursor.execute('''INSERT INTO answers 
                                 (question_id, user_id, answer, score, timestamp) 
                                 VALUES (?, ?, ?, ?, ?)''', 
                               (question_id, user_id, answer, score, now))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error recording answer: {e}")
            return False
        finally:
            self.disconnect()
    
    def update_user_policap(self, user_id, amount):
        """Update a user's policap balance"""
        if not self.connect():
            return False
            
        try:
            # Get current policap
            self.cursor.execute("SELECT policap FROM users WHERE id = ?", (user_id,))
            result = self.cursor.fetchone()
            
            if not result:
                print(f"User {user_id} not found")
                return False
                
            current_policap = result['policap']
            new_policap = current_policap + amount
            
            # Update policap and last active time
            now = datetime.now()
            self.cursor.execute('''UPDATE users 
                                 SET policap = ?, last_active = ? 
                                 WHERE id = ?''', 
                               (new_policap, now, user_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating policap: {e}")
            return False
        finally:
            self.disconnect()
    
    def add_prediction(self, user_id, bill_text, model, predicted_vote, confidence=50, explanation=None):
        """Add a vote prediction to the database"""
        if not self.connect():
            return False
            
        try:
            now = datetime.now()
            self.cursor.execute('''INSERT INTO predicted_votes 
                                 (user_id, bill_text, model, predicted_vote, confidence, explanation, timestamp) 
                                 VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                               (user_id, bill_text, model, predicted_vote, confidence, explanation, now))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding prediction: {e}")
            return None
        finally:
            self.disconnect()
    
    def get_user_daily_count(self, user_id):
        """Get the number of questions answered today by user"""
        if not self.connect():
            return 0
            
        try:
            now = datetime.now()
            self.cursor.execute('''SELECT daily_count, daily_reset 
                                 FROM users WHERE id = ?''', (user_id,))
            result = self.cursor.fetchone()
            
            if not result:
                return 0
                
            daily_count = result['daily_count']
            daily_reset = datetime.fromisoformat(result['daily_reset']) if result['daily_reset'] else now
            
            # Check if we need to reset the daily count
            if daily_reset.date() < now.date():
                self.cursor.execute('''UPDATE users 
                                     SET daily_count = 0, daily_reset = ? 
                                     WHERE id = ?''', (now, user_id))
                self.conn.commit()
                return 0
            else:
                return daily_count
        except sqlite3.Error as e:
            print(f"Error getting daily count: {e}")
            return 0
        finally:
            self.disconnect()
    
    def increment_daily_count(self, user_id):
        """Increment the daily question count for a user"""
        if not self.connect():
            return False
            
        try:
            count = self.get_user_daily_count(user_id)
            
            # Connect again as the previous method disconnected
            self.connect()
            now = datetime.now()
            self.cursor.execute('''UPDATE users 
                                 SET daily_count = ?, last_active = ? 
                                 WHERE id = ?''', 
                               (count + 1, now, user_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error incrementing daily count: {e}")
            return False
        finally:
            self.disconnect()
    
    def backup_database(self, backup_dir="backups"):
        """Create a backup copy of the database"""
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
        backup_file = os.path.join(backup_dir, f"survey_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
        
        try:
            # Connect to source database
            source_conn = sqlite3.connect(self.db_file)
            
            # Create backup connection
            backup_conn = sqlite3.connect(backup_file)
            
            # Copy data
            source_conn.backup(backup_conn)
            
            # Close connections
            backup_conn.close()
            source_conn.close()
            
            print(f"Database backed up to {backup_file}")
            return True
        except sqlite3.Error as e:
            print(f"Database backup error: {e}")
            return False


# Fix for the syntax error in the original code
if __name__ == "__main__":
    db = SurveyDatabase()
    db.init_db()
    
    # Add a default user
    db.add_user("user123")
