import sqlite3
import os
import sys
from datetime import datetime

class VoteAuditor:
    def __init__(self, db_path='senatai.db'):
        """Initialize the Vote Auditor with database connection."""
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.Senatair = None
        self.policap_spent = 0
        self.MAX_POLICAP_SPEND = 2

    def get_user(self):
        """Get the current Senatair or prompt for login."""
        self.cursor.execute("SELECT username FROM Senatairs LIMIT 1")
        Senatair = self.cursor.fetchone()
        
        if Senatair:
            self.Senatair = Senatair['username']
            print(f"Logged in as {self.Senatair}")
        else:
            username = input("Enter username: ")
            self.Senatair = username
            print(f"Logged in as {self.Senatair}")

    def get_user_policap(self):
        """Get the current policap balance for the Senatair."""
        self.cursor.execute("SELECT policap FROM Senatairs WHERE username = ?", (self.Senatair,))
        result = self.cursor.fetchone()
        
        if result:
            return result['policap']
        return 0

    def update_user_policap(self, amount):
        """Update the Senatair's policap balance."""
        current_policap = self.get_user_policap()
        new_policap = current_policap - amount
        
        if new_policap < 0:
            print("Insufficient policap balance!")
            return False
            
        self.cursor.execute("UPDATE Senatairs SET policap = ? WHERE username = ?", 
                           (new_policap, self.Senatair))
        self.conn.commit()
        return True

    def get_predictions_by_confidence(self, limit=50):
        """Get bill predictions sorted by confidence (ascending)."""
        self.cursor.execute("""
            SELECT 
                bill_text,
                predicted_vote,
                confidence,
                explanation,
                id
            FROM 
                predicted_votes
            WHERE 
                model = 'simple'
            ORDER BY 
                confidence ASC
            LIMIT ?
        """, (limit,))
        
        predictions = self.cursor.fetchall()
        return predictions

    def record_user_feedback(self, prediction_id, agrees):
        """Record the Senatair's feedback on a prediction."""
        timestamp = datetime.now()
        
        self.cursor.execute("""
            INSERT INTO prediction_feedback
            (prediction_id, username, agrees, timestamp)
            VALUES (?, ?, ?, ?)
        """, (prediction_id, self.Senatair, agrees, timestamp))
        
        self.conn.commit()
        
    def create_feedback_table_if_not_exists(self):
        """Create the prediction_feedback table if it doesn't exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS prediction_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                agrees INTEGER NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                FOREIGN KEY (prediction_id) REFERENCES predicted_votes (id),
                FOREIGN KEY (username) REFERENCES Senatairs (username)
            )
        """)
        self.conn.commit()

    def run_audit(self):
        """Run the vote auditor program."""
        self.create_feedback_table_if_not_exists()
        self.get_user()
        
        predictions = self.get_predictions_by_confidence()
        
        if not predictions:
            print("No predictions found in the database.")
            return
            
        print("\nVOTE PREDICTION AUDIT - SORTED BY CONFIDENCE (LOWEST TO HIGHEST)")
        print("=" * 70)
        
        policap_balance = self.get_user_policap()
        print(f"Current policap balance: {policap_balance}")
        print(f"Maximum policap spend: {self.MAX_POLICAP_SPEND}")
        print(f"Remaining spend allowed: {self.MAX_POLICAP_SPEND - self.policap_spent}")
        print("=" * 70)
        
        for i, prediction in enumerate(predictions, 1):
            if self.policap_spent >= self.MAX_POLICAP_SPEND:
                print("\nYou've reached your maximum policap spend limit.")
                break
                
            bill_text = prediction['bill_text']
            predicted_vote = prediction['predicted_vote']
            confidence = prediction.get('confidence', 50)  # Default to 50% if missing
            prediction_id = prediction['id']
            
            print(f"\n{i}. Bill: {bill_text}")
            print(f"   Predicted vote: {predicted_vote}")
            print(f"   Confidence: {confidence}%")
            
            user_input = input(f"\nDo you agree with this prediction? yes (cost 1 policap) / no (cost 1 policap) / skip: ").lower()
            
            if user_input in ['yes', 'no']:
                # Check if Senatair has enough policap
                if self.update_user_policap(1):
                    agrees = 1 if user_input == 'yes' else 0
                    self.record_user_feedback(prediction_id, agrees)
                    self.policap_spent += 1
                    print(f"Feedback recorded! You spent 1 policap. ({self.MAX_POLICAP_SPEND - self.policap_spent} remaining)")
                else:
                    print("You don't have enough policap to provide feedback.")
                    break
            elif user_input == 'skip':
                print("Skipped.")
            else:
                print("Invalid input, skipping.")
                
            # Show updated policap balance
            policap_balance = self.get_user_policap()
            print(f"Current policap balance: {policap_balance}")
            
            # Ask if Senatair wants to continue
            if i < len(predictions) and self.policap_spent < self.MAX_POLICAP_SPEND:
                continue_input = input("\nContinue to next bill? (y/n): ").lower()
                if continue_input != 'y':
                    break
        
        print("\nAudit complete!")
        print(f"Total policap spent: {self.policap_spent}")

if __name__ == "__main__":
    auditor = VoteAuditor()
    auditor.run_audit()
