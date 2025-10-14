import sqlite3
from datetime import datetime, date
from question_maker10 import generate_question

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
        self.init_db()

    def init_db(self):
        # Existing tables
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
                               tokens REAL DEFAULT 0,  -- Changed to REAL for decimal policap
                               last_active DATETIME)''')
        # Add new columns to users table
        try:
            self.cursor.execute('ALTER TABLE users ADD COLUMN last_reset DATE')
        except sqlite3.OperationalError:
            pass  # Column already exists
        try:
            self.cursor.execute('ALTER TABLE users ADD COLUMN daily_answer_count INTEGER DEFAULT 0')
        except sqlite3.OperationalError:
            pass  # Column already exists
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
            question_text = question_text.split('\n')[0].replace("Rate your agreement: '", "").rstrip("'")
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

    def reset_daily_count(self, user_id):
        # Get the user's last reset date
        self.cursor.execute("SELECT last_reset FROM users WHERE id = ?", (user_id,))
        last_reset = self.cursor.fetchone()[0]
        today = date.today().isoformat()

        # If last_reset is None or not today, reset the count
        if last_reset != today:
            self.cursor.execute(
                "UPDATE users SET daily_answer_count = 0, last_reset = ? WHERE id = ?",
                (today, user_id)
            )
            self.conn.commit()
            print(f"Daily count reset for user {user_id}")

    def calculate_policap(self, answer_count):
        if answer_count < 10:  # First 10 answers
            return 1.0
        elif answer_count < 100:  # Answers 11-100
            # Linear decrease from 1 to 0.01
            # Formula: policap = 1 - (count - 10) * (1 - 0.01) / (100 - 10)
            return round(1.0 - (answer_count - 10) * (1.0 - 0.01) / 90, 3)
        elif answer_count < 200:  # Answers 101-200
            return 0.01
        else:  # Answers 201+
            return 0.001

    def ask_question(self, user_id):
        # Reset daily count if needed
        self.reset_daily_count(user_id)

        # Get current daily answer count
        self.cursor.execute("SELECT daily_answer_count FROM users WHERE id = ?", (user_id,))
        answer_count = self.cursor.fetchone()[0]

        # Fetch a question
        self.cursor.execute("""
            SELECT id, question_text, question_type 
            FROM questions 
            WHERE id NOT IN (SELECT question_id FROM answers WHERE user_id = ?)
        """, (user_id,))
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
            print("Scale: 1=Strongly disagree, 2=Disagree, 3=Neutral, 4=Agree, 5=Strongly agree")
            answer = input("Answer (1-5): ")
            score = int(answer) if answer.isdigit() and 1 <= int(answer) <= 5 else None
        
        # Calculate policap
        policap = self.calculate_policap(answer_count)
        
        # Update answer count and tokens
        self.cursor.execute(
            "INSERT INTO answers (question_id, answer, score, user_id, timestamp) VALUES (?, ?, ?, ?, ?)",
            (q_id, answer, score, user_id, datetime.now())
        )
        self.cursor.execute(
            "UPDATE users SET tokens = tokens + ?, daily_answer_count = daily_answer_count + 1, last_active = ? WHERE id = ?",
            (policap, datetime.now(), user_id)
        )
        self.conn.commit()
        print(f"Question asked and answer recorded! Earned {policap} policap.")
        return True

if __name__ == "__main__":
    system = SurveySystem()
    user_id = "user123"
    system.cursor.execute("INSERT OR IGNORE INTO users (id, last_active) VALUES (?, ?)",
                         (user_id, datetime.now()))
    system.conn.commit()
    print(f"Logged in as {user_id}")
    
    # Ask 5 questions (for testing; you can increase this to test the tiers)
    for _ in range(5):
        system.generate_and_store_question()
        if not system.ask_question(user_id):
            break
    
    # Show total policap and daily answer count
    system.cursor.execute("SELECT tokens, daily_answer_count FROM users WHERE id = ?", (user_id,))
    total_policap, daily_count = system.cursor.fetchone()
    print(f"Total policap: {total_policap}")
    print(f"Answers today: {daily_count}")
