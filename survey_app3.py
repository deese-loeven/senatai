import sqlite3
from datetime import datetime
from THEMES import THEMES  # Import your themes

class SurveySystem:
    def __init__(self, db_name="survey_data.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS questions
                              (id INTEGER PRIMARY KEY AUTOINCREMENT,
                               question_text TEXT,
                               question_type TEXT,
                               theme TEXT,
                               timestamp DATETIME)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS answers
                              (id INTEGER PRIMARY KEY AUTOINCREMENT,
                               question_id INTEGER,
                               answer TEXT,
                               score INTEGER,
                               user_id TEXT,
                               timestamp DATETIME,
                               FOREIGN KEY(question_id) REFERENCES questions(id))''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                              (id TEXT PRIMARY KEY,
                               tokens INTEGER DEFAULT 0,
                               last_active DATETIME)''')
        self.conn.commit()
        print("Database initialized successfully!")

    def detect_theme(self, question_text):
        question_text = question_text.lower()
        for theme, keywords in THEMES.items():
            if any(keyword in question_text for keyword in keywords):
                return theme
        return "general"

    def generate_and_store_question(self):
        # Example question from your question_maker10.py output
        question_text = "Should Canada prioritize free speech protections over senior benefits?"
        question_type = "yes_no"  # Adjust based on your question_maker logic
        theme = self.detect_theme(question_text)
        timestamp = datetime.now()
        self.cursor.execute(
            "INSERT INTO questions (question_text, question_type, theme, timestamp) VALUES (?, ?, ?, ?)",
            (question_text, question_type, theme, timestamp)
        )
        self.conn.commit()
        print(f"Stored question: '{question_text}' with theme '{theme}'")

    def ask_question(self, user_id):
        # Check for unanswered questions
        self.cursor.execute("""
            SELECT id, question_text, question_type 
            FROM questions 
            WHERE id NOT IN (SELECT question_id FROM answers WHERE user_id = ?)
        """, (user_id,))
        question = self.cursor.fetchone()
        if not question:
            print("No questions available or you've answered them all!")
            return
        
        q_id, q_text, q_type = question
        print(f"Question: {q_text}")
        if q_type == "yes_no":
            answer = input("Answer (yes/no): ").lower()
            score = None
        else:  # scale_1_to_5
            answer = input("Answer (1-5): ")
            score = int(answer) if answer.isdigit() and 1 <= int(answer) <= 5 else None
        
        self.cursor.execute(
            "INSERT INTO answers (question_id, answer, score, user_id, timestamp) VALUES (?, ?, ?, ?, ?)",
            (q_id, answer, score, user_id, datetime.now())
        )
        # Award 1 policap
        self.cursor.execute("UPDATE users SET tokens = tokens + 1, last_active = ? WHERE id = ?",
                           (datetime.now(), user_id))
        self.conn.commit()
        print("Question asked and answer recorded!")

# Simulate a user login and interaction
if __name__ == "__main__":
    system = SurveySystem()
    user_id = "user123"
    # Ensure user exists
    system.cursor.execute("INSERT OR IGNORE INTO users (id, last_active) VALUES (?, ?)",
                         (user_id, datetime.now()))
    system.conn.commit()
    print(f"Logged in as {user_id}")
    system.generate_and_store_question()
    system.ask_question(user_id)
