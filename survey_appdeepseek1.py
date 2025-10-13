import sqlite3
import importlib
import glob
from datetime import datetime, date
import random
import uuid

class SurveySystem:
    def __init__(self, db_name="survey_data.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._init_db()
        self.question_makers = self._discover_question_makers()
        self.current_maker = None

    def _init_db(self):
        """Initialize database tables"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Senatairs (
                id TEXT PRIMARY KEY,
                policaps REAL DEFAULT 0,
                last_active TEXT
            )""")
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                question_id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_text TEXT,
                maker_source TEXT
            )""")
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS answers (
                answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER,
                id TEXT,
                answer TEXT,
                score REAL,
                timestamp TEXT,
                FOREIGN KEY(question_id) REFERENCES questions(question_id),
                FOREIGN KEY(id) REFERENCES Senatairs(id)
            )""")
        self.conn.commit()

    def _discover_question_makers(self):
        """Find and import all question_maker*.py files"""
        makers = {}
        for file in glob.glob("question_maker*.py"):
            try:
                module_name = file[:-3]  # Remove .py
                module = importlib.import_module(module_name)
                if hasattr(module, 'generate_question'):
                    maker_name = f"Maker {file[13:-3]}"  # Extract number
                    makers[maker_name] = module.generate_question
                    print(f"✓ Loaded {maker_name}")
            except Exception as e:
                print(f"× Error loading {file}: {str(e)}")
        return makers

    def select_question_maker(self):
        """Let Senatair select which question maker to use"""
        print("\nAvailable Question Makers:")
        for i, name in enumerate(self.question_makers.keys(), 1):
            print(f"{i}. {name}")
        
        while True:
            choice = input("\nSelect a question maker (number): ")
            if choice.isdigit() and 1 <= int(choice) <= len(self.question_makers):
                maker_name = list(self.question_makers.keys())[int(choice)-1]
                self.current_maker = self.question_makers[maker_name]
                print(f"\nSelected: {maker_name}")
                return maker_name
            print("Invalid choice. Please try again.")

    def generate_question(self):
        """Generate and store a new question"""
        if not self.current_maker:
            self.select_question_maker()
            
        question_text = self.current_maker()
        self.cursor.execute(
            "INSERT INTO questions (question_text, maker_source) VALUES (?, ?)",
            (question_text, str(self.current_maker.__module__))
        )
        self.conn.commit()
        return question_text

    def ask_question(self, id):
        """Present a question and record the answer"""
        # Get an unanswered question
        self.cursor.execute("""
            SELECT question_id, question_text FROM questions
            WHERE question_id NOT IN (
                SELECT question_id FROM answers WHERE id = ?
            )
            ORDER BY RANDOM() LIMIT 1
        """, (id,))
        
        question = self.cursor.fetchone()
        if not question:
            print("\nNo more unanswered questions!")
            return False
            
        q_id, q_text = question
        print(f"\nQuestion: {q_text}")
        
        # Handle different question types
        if "Rate your agreement" in q_text:
            print("(1=Strongly disagree, 5=Strongly agree)")
            while True:
                answer = input("Your answer (1-5): ")
                if answer.isdigit() and 1 <= int(answer) <= 5:
                    score = int(answer)
                    break
                print("Please enter a number 1-5")
        else:
            while True:
                answer = input("Your answer (yes/no): ").lower()
                if answer in ['yes', 'no', 'y', 'n']:
                    score = 1 if answer in ['yes', 'y'] else 0
                    break
                print("Please answer 'yes' or 'no'")
        
        # Record answer
        self.cursor.execute("""
            INSERT INTO answers 
            (question_id, id, answer, score, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (q_id, id, answer, score, datetime.now()))
        
        # Update Senatair tokens
        self.cursor.execute("""
            UPDATE Senatairs SET policaps = policaps + 1, last_active = ?
            WHERE id = ?
        """, (datetime.now(), id))
        
        self.conn.commit()
        print("✓ Answer recorded! +1 policap")
        return True

def get_id():
    """Get or create Senatair ID"""
    while True:
        id = input("\nEnter your Senatair ID (3-20 chars): ").strip()
        if 3 <= len(id) <= 20:
            return id
        print("ID must be 3-20 characters")

def main_menu():
    print("\nMAIN MENU")
    print("1. Answer questions")
    print("2. Change question maker")
    print("3. View stats")
    print("4. Exit")
    return input("Choose an option: ")

if __name__ == "__main__":
    system = SurveySystem()
    id = get_id()
    
    # Create Senatair if new
    system.cursor.execute(
        "INSERT OR IGNORE INTO Senatairs (id, last_active) VALUES (?, ?)",
        (id, datetime.now())
    )
    system.conn.commit()
    
    # Main loop
    while True:
        choice = main_menu()
        
        if choice == "1":  # Answer questions
            for _ in range(3):  # Ask 3 questions at a time
                if not system.ask_question(id):
                    break
                    
        elif choice == "2":  # Change maker
            system.select_question_maker()
            
        elif choice == "3":  # View stats
            system.cursor.execute("""
                SELECT COUNT(*) FROM answers WHERE id = ?
            """, (id,))
            answers = system.cursor.fetchone()[0]
            
            system.cursor.execute("""
                SELECT policaps FROM Senatairs WHERE id = ?
            """, (id,))
            policaps = system.cursor.fetchone()[0]
            
            print(f"\nYour Stats:")
            print(f"- Questions answered: {answers}")
            print(f"- Total policaps earned: {policaps}")
            
        elif choice == "4":  # Exit
            print("\nThanks for participating!")
            break
            
        else:
            print("Invalid choice")
