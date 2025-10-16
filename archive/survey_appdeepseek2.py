import sqlite3
from datetime import datetime, date
import uuid
from question_maker10 import generate_question

class SurveySystem:
    def __init__(self, db_name="survey_data.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        # No table creation - using existing schema

    def detect_theme(self, question_text):
        # Your existing theme detection logic
        pass

    def generate_and_store_question(self):
        question_text = generate_question()
        if "Rate your agreement" in question_text:
            question_type = "scale_1_to_5"
            question_text = question_text.split('\n')[0].replace("Rate your agreement: '", "").rstrip("'")
        else:
            question_type = "yes_no"
        
        theme = self.detect_theme(question_text)
        
        self.cursor.execute(
            """INSERT INTO questions 
               (question_text, question_type, theme) 
               VALUES (?, ?, ?)""",
            (question_text, question_type, theme)
        )
        self.conn.commit()
        print(f"Stored question: {question_text}")

    def reset_daily_count(self, Senatair_id):
        today = date.today().isoformat()
        self.cursor.execute(
            """UPDATE Senatairs 
               SET daily_answer_count = 0, 
                   last_reset = ? 
               WHERE id = ? AND (last_reset IS NULL OR last_reset != ?)""",
            (today, Senatair_id, today)
        )
        self.conn.commit()

    def calculate_policap(self, answer_count):
        # Your existing policap calculation
        pass

    def ask_question(self, Senatair_id):
        self.reset_daily_count(Senatair_id)

        # Get unanswered question matching your schema
        self.cursor.execute(
            """SELECT q.id, q.question_text, q.question_type 
               FROM questions q
               WHERE q.id NOT IN (
                   SELECT a.question_id 
                   FROM answers a 
                   WHERE a.Senatair_id = ?
               )
               ORDER BY RANDOM() 
               LIMIT 1""",
            (Senatair_id,)
        )
        question = self.cursor.fetchone()
        
        if not question:
            print("No questions available!")
            return False

        q_id, q_text, q_type = question
        print(f"\nQuestion: {q_text}")
        
        if q_type == "scale_1_to_5":
            print("(1=Strongly disagree, 5=Strongly agree)")
            while True:
                answer = input("Your answer (1-5): ")
                if answer.isdigit() and 1 <= int(answer) <= 5:
                    score = int(answer)
                    break
                print("Please enter 1-5")
        else:
            while True:
                answer = input("Your answer (yes/no): ").lower()
                if answer in ['yes', 'no', 'y', 'n']:
                    score = 1 if answer in ['yes', 'y'] else 0
                    break
                print("Please answer yes/no")

        # Record answer matching your schema
        self.cursor.execute(
            """INSERT INTO answers 
               (question_id, answer, score, Senatair_id) 
               VALUES (?, ?, ?, ?)""",
            (q_id, answer, score, Senatair_id)
        )
        
        # Update Senatair stats
        self.cursor.execute(
            """UPDATE Senatairs 
               SET policap = policap + ?,
                   daily_answer_count = daily_answer_count + 1,
                   last_active = ?
               WHERE id = ?""",
            (self.calculate_policap(self.get_answer_count(Senatair_id)), 
            datetime.now(), 
            Senatair_id)
        )
        self.conn.commit()
        return True

    def get_answer_count(self, Senatair_id):
        self.cursor.execute(
            "SELECT COUNT(*) FROM answers WHERE Senatair_id = ?",
            (Senatair_id,)
        )
        return self.cursor.fetchone()[0]

def get_user_id():
    while True:
        Senatair_id = input("Enter Senatair ID: ").strip()
        if 3 <= len(Senatair_id) <= 30:
            return Senatair_id
        print("ID must be 3-30 characters")

if __name__ == "__main__":
    system = SurveySystem()
    Senatair_id = get_user_id()
    
    # Initialize Senatair if new
    system.cursor.execute(
        "INSERT OR IGNORE INTO Senatairs (id, last_active) VALUES (?, ?)",
        (Senatair_id, datetime.now())
    )
    system.conn.commit()
    
    # Main interaction loop
    while True:
        system.generate_and_store_question()
        if not system.ask_question(Senatair_id):
            break
            
        # Show stats
        system.cursor.execute(
            "SELECT policap, daily_answer_count FROM Senatairs WHERE id = ?",
            (Senatair_id,)
        )
        policap, daily_count = system.cursor.fetchone()
        print(f"\nStats: {policap} policap, {daily_count} answers today")
