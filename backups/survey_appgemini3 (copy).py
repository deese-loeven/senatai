import sqlite3
from datetime import datetime, date
from question_maker10 import generate_question
import uuid  # import uuid for unique token generation.

# Define THEMES directly
THEMES = {
    "economic": ["taxation", "economic growth", "small business support",
                 "inflation control", "wage policies"],
    "social": ["healthcare access", "education funding", "child care programs",
                "senior benefits", "housing affordability"],
    "rights": ["free speech protections", "digital privacy", "gun ownership rights",
                "gender equality", "indigenous rights"],
    "environment": ["climate change", "clean energy", "wildlife conservation",
                    "pollution reduction", "sustainable development"]
}

class SurveySystem:
    def __init__(self, db_name="survey_data.db"):
    self.conn = sqlite3.connect(db_name)
    self.cursor = self.conn.cursor()
    
    # Create tables if they don't exist
    self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Questions (
            question_id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_text TEXT,
            question_maker TEXT,
            bill_id INTEGER
        )
    """)
    
    self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            policaps REAL DEFAULT 0,
            daily_answer_count INTEGER DEFAULT 0,
            last_active TEXT,
            last_reset TEXT
        )
    """)
    
    self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Answers (
            answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER,
            answer_text TEXT,
            score INTEGER,
            id TEXT,
            policap REAL,
            FOREIGN KEY(question_id) REFERENCES Questions(question_id),
            FOREIGN KEY(id) REFERENCES users(id)
        )
    """)
    self.conn.commit()

    def detect_theme(self, question_text):
        question_text = question_text.lower()
        for theme, keywords in THEMES.items():
            if any(keyword in question_text for keyword in keywords):
                return theme
        return "general"

    def generate_and_store_question(self):
        question_text = generate_question()
        if "Rate your agreement" in question_text:
            question_type = "scale_1_to_5"
            question_text = question_text.split('\n')[0].replace("Rate your agreement: '", "").rstrip("'")
        else:
            question_type = "yes_no"
        theme = self.detect_theme(question_text)
        timestamp = datetime.now()
        # insert questions into the Questions table.
        self.cursor.execute(
            "INSERT INTO Questions (question_text, question_maker, bill_id) VALUES (?, ?, NULL)",
            (question_text, "Survey App")
        )
        self.conn.commit()
        print(f"Stored question: '{question_text}' with theme '{theme}'")

    def reset_daily_count(self, id):
        self.cursor.execute("SELECT last_reset FROM Users WHERE id = ?", (id,))
        last_reset = self.cursor.fetchone()[0]
        today = date.today().isoformat()

        if last_reset != today:
            self.cursor.execute(
                "UPDATE users SET daily_answer_count = 0, last_reset = ? WHERE id = ?",
                (today, id)
            )
            self.conn.commit()
            print(f"Daily count reset for user {id}")

    def calculate_policap(self, answer_count):
        if answer_count < 10:
            return 1.0
        elif answer_count < 100:
            return round(1.0 - (answer_count - 10) * (1.0 - 0.01) / 90, 3)
        elif answer_count < 200:
            return 0.01
        else:
            return 0.001

    def ask_question(self, id):
        self.reset_daily_count(id)

        self.cursor.execute("SELECT daily_answer_count FROM Users WHERE id = ?", (id,))
        answer_count = self.cursor.fetchone()[0]

        self.cursor.execute("""
            SELECT question_id, question_text FROM Questions
            WHERE question_id NOT IN (SELECT question_id FROM Answers WHERE id = ?)
        """, (id,))
        question = self.cursor.fetchone()
        if not question:
            print("No questions available or you've answered them all!")
            return False

        q_id, q_text = question
        print(f"Question: {q_text}")
        if "scale_1_to_5" in q_text:  # detect the type of question from the question text.
            print("Scale: 1=Strongly disagree, 2=Disagree, 3=Neutral, 4=Agree, 5=Strongly agree")
            answer = input("Answer (1-5): ")
            score = int(answer) if answer.isdigit() and 1 <= int(answer) <= 5 else None
        else:
            answer = input("Answer (yes/no): ").lower()
            score = None

        policap = self.calculate_policap(answer_count)
        token = str(uuid.uuid4())  # generate a unique token.
        self.cursor.execute(
            "INSERT INTO Answers (question_id, answer_text, score, id, policap) VALUES (?, ?, ?, ?, ?)",
            (q_id, answer, score, id, policap)
        )
        self.cursor.execute(
            "UPDATE users SET policaps = policaps + ?, daily_answer_count = daily_answer_count + 1, last_active = ? WHERE id = ?",
            (policap, datetime.now(), id)
        )
        self.conn.commit()
        print(f"Question asked and answer recorded! Earned {policap} policap.")
        return True

def get_id(system):
    while True:
        id = input("Please enter your unique user ID (3-30 characters): ").strip()
        if id:
            if 3 <= len(id) <= 30:
                return id
            else:
                print("User ID must be between 3 and 30 characters.")
        else:
            print("User ID cannot be empty. Please try again.")

if __name__ == "__main__":
    system = SurveySystem()
    id = get_id(system)

    # Check if user already exists
    system.cursor.execute("SELECT id FROM users WHERE id = ?", (id,))
    existing_user = system.cursor.fetchone()

    system.cursor.execute("INSERT OR IGNORE INTO users (id, last_active) VALUES (?, ?)",
                        (id, datetime.now()))
    system.conn.commit()

    if existing_user:
        print(f"Welcome back, {id}!")
    else:
        print(f"New user created: {id}. Welcome!")

    for _ in range(5):
        system.generate_and_store_question()
        if not system.ask_question(id):
            break

    system.cursor.execute("SELECT policaps, daily_answer_count FROM users WHERE id = ?", (id,))
    total_policap, daily_count = system.cursor.fetchone()
    print(f"Total policap: {total_policap}")
    print(f"Answers today: {daily_count}")
