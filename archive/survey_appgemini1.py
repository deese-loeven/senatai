import sqlite3
from datetime import datetime, date
from question_maker10 import generate_question
import uuid #import uuid for unique token generation.

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
    def __init__(self, db_name="mydatabase.db"): #change to mydatabase.db
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        #init_db is not needed, as the database is already created.

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
        #insert questions into the Questions table.
        self.cursor.execute(
            "INSERT INTO Questions (question_text, question_maker, bill_id) VALUES (?, ?, NULL)", #bill_id is null for now.
            (question_text, "Survey App") #change question maker to something accurate.
        )
        self.conn.commit()
        print(f"Stored question: '{question_text}' with theme '{theme}'")

    def reset_daily_count(self, Senatair_id):
        self.cursor.execute("SELECT last_reset FROM Users WHERE id = ?", (Senatair_id,))
        last_reset = self.cursor.fetchone()[0]
        today = date.today().isoformat()

        if last_reset != today:
            self.cursor.execute(
                "UPDATE Users SET daily_answer_count = 0, last_reset = ? WHERE id = ?",
                (today, Senatair_id)
            )
            self.conn.commit()
            print(f"Daily count reset for Senatair {Senatair_id}")

    def calculate_policap(self, answer_count):
        if answer_count < 10:
            return 1.0
        elif answer_count < 100:
            return round(1.0 - (answer_count - 10) * (1.0 - 0.01) / 90, 3)
        elif answer_count < 200:
            return 0.01
        else:
            return 0.001

    def ask_question(self, Senatair_id):
        self.reset_daily_count(Senatair_id)

        self.cursor.execute("SELECT daily_answer_count FROM Users WHERE id = ?", (Senatair_id,))
        answer_count = self.cursor.fetchone()[0]

        self.cursor.execute("""
            SELECT question_id, question_text FROM Questions
            WHERE question_id NOT IN (SELECT question_id FROM Answers WHERE Senatair_id = ?)
        """, (Senatair_id,))
        question = self.cursor.fetchone()
        if not question:
            print("No questions available or you've answered them all!")
            return False

        q_id, q_text = question
        print(f"Question: {q_text}")
        if "scale_1_to_5" in q_text: #detect the type of question from the question text.
            print("Scale: 1=Strongly disagree, 2=Disagree, 3=Neutral, 4=Agree, 5=Strongly agree")
            answer = input("Answer (1-5): ")
            score = int(answer) if answer.isdigit() and 1 <= int(answer) <= 5 else None
        else:
            answer = input("Answer (yes/no): ").lower()
            score = None

        policap = self.calculate_policap(answer_count)
        token = str(uuid.uuid4()) #generate a unique token.
        self.cursor.execute(
            "INSERT INTO Answers (question_id, answer_text, score, Senatair_id, token) VALUES (?, ?, ?, ?, ?)",
            (q_id, answer, score, Senatair_id, token)
        )
        self.cursor.execute(
            "UPDATE Users SET tokens = tokens + ?, daily_answer_count = daily_answer_count + 1, last_active = ? WHERE id = ?",
            (policap, datetime.now(), Senatair_id)
        )
        self.conn.commit()
        print(f"Question asked and answer recorded! Earned {policap} policap.")
        return True

if __name__ == "__main__":
    system = SurveySystem()
    Senatair_id = "user123"
    system.cursor.execute("INSERT OR IGNORE INTO Users (id, last_active) VALUES (?, ?)",
                        (Senatair_id, datetime.now()))
    system.conn.commit()
    print(f"Logged in as {Senatair_id}")

    for _ in range(5):
        system.generate_and_store_question()
        if not system.ask_question(Senatair_id):
            break

    system.cursor.execute("SELECT tokens, daily_answer_count FROM Users WHERE id = ?", (Senatair_id,))
    total_policap, daily_count = system.cursor.fetchone()
    print(f"Total policap: {total_policap}")
    print(f"Answers today: {daily_count}")
