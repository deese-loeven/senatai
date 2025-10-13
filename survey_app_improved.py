import sqlite3
import datetime
from question_maker10 import generate_question

class SurveySystem:
    def __init__(self, db_name="mydatabase.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        print("Senatai Civic Platform - Welcome!")
        
    def ask_question(self, user_id):
        """Ask a question and record the answer"""
        try:
            # Generate question
            question = generate_question()
            print(f"\nQuestion: {question}")
            
            # Handle different question types
            if "?" in question and ("how" in question.lower() or "feel" in question.lower()):
                print("(Please answer with your opinion, then press Enter)")
                answer = input("Your response: ").strip()
            else:
                answer = input("Answer (support/oppose): ").strip().lower()
                if answer not in ['support', 'oppose']:
                    print("Please answer 'support' or 'oppose'")
                    return False
            
            # Simple policap reward
            self.cursor.execute(
                "UPDATE Senatairs SET policaps = policaps + 1, last_active = ? WHERE user_id = ?",
                (datetime.datetime.now(), user_id)
            )
            self.conn.commit()
            
            print(f"✓ Response recorded! +1 Policap awarded.")
            return True
            
        except Exception as e:
            print(f"Error: {e}")
            return False

# Main execution
if __name__ == "__main__":
    system = SurveySystem()
    user_id = "user123"
    
    # Ensure user exists
    system.cursor.execute("INSERT OR IGNORE INTO Senatairs (user_id, username) VALUES (?, ?)", (user_id, user_id))
    system.conn.commit()
    
    print(f"Welcome, Senatair {user_id}!")
    
    if system.ask_question(user_id):
        # Show stats
        system.cursor.execute("SELECT policaps FROM Senatairs WHERE user_id = ?", (user_id,))
        result = system.cursor.fetchone()
        if result:
            policaps = result[0]
            print(f"💰 Your Policap balance: {policaps}")
    
    system.conn.close()
