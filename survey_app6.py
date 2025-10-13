import sqlite3
import datetime
from question_maker10 import generate_question

class SurveySystem:
    def __init__(self, db_name="mydatabase.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        print("Database initialized successfully!")
        
    def reset_daily_count(self, user_id):
        """Reset daily answer count if it's a new day"""
        try:
            self.cursor.execute("SELECT last_reset FROM Senatairs WHERE user_id = ?", (user_id,))
            result = self.cursor.fetchone()
            
            if result and result[0]:
                last_reset = datetime.datetime.strptime(result[0], '%Y-%m-%d').date()
                today = datetime.datetime.now().date()
                if last_reset < today:
                    self.cursor.execute(
                        "UPDATE Senatairs SET daily_answer_count = 0, last_reset = ? WHERE user_id = ?",
                        (today, user_id)
                    )
                    self.conn.commit()
                    print("Daily count reset!")
            else:
                today = datetime.datetime.now().date()
                self.cursor.execute(
                    "UPDATE Senatairs SET last_reset = ? WHERE user_id = ?",
                    (today, user_id)
                )
                self.conn.commit()
        except Exception as e:
            print(f"Error resetting daily count: {e}")
    
    def calculate_policaps(self, answer_count):
        """Calculate policaps with diminishing returns"""
        if answer_count < 10:
            return 1.0
        elif answer_count < 100:
            return max(1.0 - (answer_count - 10) * (0.99 / 90), 0.01)
        else:
            return 0.01
    
    def ask_question(self, user_id):
        """Ask a question and record the answer"""
        try:
            # Reset daily count if needed
            self.reset_daily_count(user_id)
            
            # Generate and store question
            question = generate_question()
            theme = "general"
            
            self.cursor.execute(
                "INSERT INTO Questions (bill_id, question_text, question_maker) VALUES (?, ?, ?)",
                (1, question, "question_maker10")
            )
            self.conn.commit()
            print(f"Stored question: '{question}' with theme '{theme}'")
            
            # Ask the question
            print(f"Question: {question}")
            answer = input("Answer (yes/no): ").strip().lower()
            
            if answer not in ['yes', 'no']:
                print("Invalid answer. Please answer 'yes' or 'no'.")
                return False
            
            # Get current answer count
            self.cursor.execute("SELECT daily_answer_count FROM Senatairs WHERE user_id = ?", (user_id,))
            result = self.cursor.fetchone()
            answer_count = result[0] if result else 0
            
            # Calculate policap reward
            policap_reward = self.calculate_policaps(answer_count)
            
            # Update user stats
            self.cursor.execute(
                "UPDATE Senatairs SET policaps = policaps + ?, daily_answer_count = daily_answer_count + 1, last_active = ? WHERE user_id = ?",
                (policap_reward, datetime.datetime.now(), user_id)
            )
            self.conn.commit()
            
            print(f"Question asked and answer recorded! Earned {policap_reward} policaps.")
            return True
            
        except Exception as e:
            print(f"Error in ask_question: {e}")
            return False

# Main execution
if __name__ == "__main__":
    system = SurveySystem()
    user_id = "user123"
    
    # Ensure user exists
    system.cursor.execute("INSERT OR IGNORE INTO Senatairs (user_id, username) VALUES (?, ?)", (user_id, user_id))
    system.conn.commit()
    
    print(f"Logged in as {user_id}")
    
    if system.ask_question(user_id):
        # Show stats
        system.cursor.execute("SELECT policaps, daily_answer_count FROM Senatairs WHERE user_id = ?", (user_id,))
        result = system.cursor.fetchone()
        if result:
            policaps, daily_count = result
            print(f"Total policaps: {policaps}")
            print(f"Questions answered today: {daily_count}")
    
    system.conn.close()
