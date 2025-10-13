import sqlite3
from datetime import datetime
from question_maker10 import generate_question  # Import your question generator

# Define THEMES directly since THEMES.py might not be set up
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
                               Senatair_id TEXT,
                               timestamp DATETIME,
                               FOREIGN KEY(question_id) REFERENCES questions(id))''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Senatairs
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
        question_text = generate_question()
        if "Rate your agreement" in question_text:
            question_type = "scale_1_to_5"
        else:
            question_type = "yes_no"
        theme = self.detect_theme(question_text)
        timestamp = datetime.now()
        self.cursor.execute(
            "INSERT INTO questions (question_text, question_type, theme, timestamp) VALUES (?, ?, ?, ?)",
            (question_text, question_type, theme, timestamp)
        )
        self.conn.commit()
        print(f"Stored question: '{question_text}' with theme '{theme}'")

    def ask_question(self, Senatair_id):
        self.cursor.execute("""
            SELECT id, question_text, question_type 
            FROM questions 
            WHERE id NOT IN (SELECT question_id FROM answers WHERE Senatair_id = ?)
        """, (Senatair_id,))
        question = self.cursor.fetchone()
        if not question:
            print("No questions available or you've answered them all!")
            return False
        
        q_id, q_text, q_type = question
        print(f"Question: {q_text}")
        if q_type == "yes_no":
            answer = input("Answer (yes/no): ").lower()
            score = None
        else:  # scale_1_to_5
            answer = input("Answer (1-5): ")
            score = int(answer) if answer.isdigit() and 1 <= int(answer) <= 5 else None
        
        # Calculate policap with diminishing returns
        self.cursor.execute("SELECT COUNT(*) FROM answers WHERE Senatair_id = ?", (Senatair_id,))
        answer_count = self.cursor.fetchone()[0]
        policap = max(5 - answer_count, 1)  # 5, 4, 3, 2, 1, then 1 forever
        
        self.cursor.execute(
            "INSERT INTO answers (question_id, answer, score, Senatair_id, timestamp) VALUES (?, ?, ?, ?, ?)",
            (q_id, answer, score, Senatair_id, datetime.now())
        )
        self.cursor.execute("UPDATE Senatairs SET tokens = tokens + ?, last_active = ? WHERE id = ?",
                           (policap, datetime.now(), Senatair_id))
        self.conn.commit()
        print(f"Question asked and answer recorded! Earned {policap} policap.")
        return True

if __name__ == "__main__":
    system = SurveySystem()
    Senatair_id = "user123"
    system.cursor.execute("INSERT OR IGNORE INTO Senatairs (id, last_active) VALUES (?, ?)",
                         (Senatair_id, datetime.now()))
    system.conn.commit()
    print(f"Logged in as {Senatair_id}")
    
    # Ask 5 questions
    for _ in range(5):
        system.generate_and_store_question()
        if not system.ask_question(Senatair_id):
            break
    
    # Show total policap
    system.cursor.execute("SELECT tokens FROM Senatairs WHERE id = ?", (Senatair_id,))
    total_policap = system.cursor.fetchone()[0]
    print(f"Total policap: {total_policap}")
