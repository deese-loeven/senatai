import sqlite3
from datetime import datetime
import pandas as pd

# 1. Database Setup with Voting System
def init_db():
    conn = sqlite3.connect('political_predictor.db')
    c = conn.cursor()
    
    # Legislative Bills Table
    c.execute('''CREATE TABLE IF NOT EXISTS bills
                 (bill_id TEXT PRIMARY KEY,
                  title TEXT,
                  description TEXT,
                  predicted_outcome REAL,
                  actual_outcome REAL,
                  status TEXT)''')
    
    # User Voting Power
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id TEXT PRIMARY KEY,
                  tokens INTEGER DEFAULT 10,  # Starting tokens
                  last_vote DATETIME)''')
    
    # Votes Table (Token Expenditure)
    c.execute('''CREATE TABLE IF NOT EXISTS votes
                 (vote_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  bill_id TEXT,
                  user_id TEXT,
                  position TEXT CHECK(position IN ('for', 'against')),
                  tokens_spent INTEGER,
                  timestamp DATETIME,
                  FOREIGN KEY(bill_id) REFERENCES bills(bill_id),
                  FOREIGN KEY(user_id) REFERENCES users(user_id))''')
    
    # Survey Answers (Token Earnings)
    c.execute('''CREATE TABLE IF NOT EXISTS survey_answers
                 (answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  question_id INTEGER,
                  user_id TEXT,
                  answer TEXT,
                  tokens_earned INTEGER DEFAULT 1,
                  timestamp DATETIME,
                  FOREIGN KEY(user_id) REFERENCES users(user_id))''')
    
    conn.commit()
    conn.close()

# 2. Token Economy Implementation
class TokenSystem:
    def __init__(self):
        self.conn = sqlite3.connect('political_predictor.db')
    
    def earn_tokens(self, user_id, amount=1):
        """Reward for answering surveys"""
        c = self.conn.cursor()
        c.execute('''INSERT OR IGNORE INTO users (user_id, tokens) VALUES (?, 10)''', (user_id,))
        c.execute('''UPDATE users SET tokens = tokens + ? WHERE user_id = ?''', (amount, user_id))
        self.conn.commit()
        return c.execute('''SELECT tokens FROM users WHERE user_id = ?''', (user_id,)).fetchone()[0]
    
    def spend_tokens(self, user_id, bill_id, position, amount):
        """Spend tokens to influence legislation"""
        if amount <= 0:
            return False
        
        c = self.conn.cursor()
        c.execute('''SELECT tokens FROM users WHERE user_id = ?''', (user_id,))
        balance = c.fetchone()[0]
        
        if balance >= amount:
            c.execute('''UPDATE users SET tokens = tokens - ?, last_vote = ? WHERE user_id = ?''',
                     (amount, datetime.now(), user_id))
            c.execute('''INSERT INTO votes (bill_id, user_id, position, tokens_spent, timestamp)
                         VALUES (?, ?, ?, ?, ?)''',
                         (bill_id, user_id, position, amount, datetime.now()))
            self.update_bill_prediction(bill_id)
            self.conn.commit()
            return True
        return False
    
    def update_bill_prediction(self, bill_id):
        """Adjust prediction based on token votes"""
        c = self.conn.cursor()
        
        # Get current prediction
        c.execute('''SELECT predicted_outcome FROM bills WHERE bill_id = ?''', (bill_id,))
        current_pred = c.fetchone()[0]
        
        # Get aggregate votes
        c.execute('''SELECT position, SUM(tokens_spent) FROM votes WHERE bill_id = ? GROUP BY position''', (bill_id,))
        votes = {'for':0, 'against':0}
        for pos, amount in c.fetchall():
            votes[pos] = amount
        
        # Calculate new prediction (simple weighted average example)
        total_votes = votes['for'] + votes['against']
        if total_votes > 0:
            vote_ratio = votes['for'] / total_votes
            new_pred = (current_pred * 0.7) + (vote_ratio * 0.3)  # 30% weight to token votes
            c.execute('''UPDATE bills SET predicted_outcome = ? WHERE bill_id = ?''', (new_pred, bill_id))
            self.conn.commit()

# 3. Integration with Your Existing Systems
class PoliticalPredictor:
    def __init__(self):
        self.token_system = TokenSystem()
        init_db()
    
    def answer_survey(self, user_id, question_id, answer):
        """Answer a question and earn tokens"""
        # Store answer (using your existing question system)
        self.token_system.earn_tokens(user_id)
        # Add to training data for model updates
        self._add_to_training_data(question_id, answer, user_id)
    
    def vote_on_bill(self, user_id, bill_id, position, tokens_to_spend):
        """Spend tokens to influence a bill"""
        return self.token_system.spend_tokens(user_id, bill_id, position, tokens_to_spend)
    
    def get_bill_prediction(self, bill_id):
        """Get current prediction including token influence"""
        conn = sqlite3.connect('political_predictor.db')
        c = conn.cursor()
        c.execute('''SELECT predicted_outcome FROM bills WHERE bill_id = ?''', (bill_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None
    
    def _add_to_training_data(self, question_id, answer, user_id):
        """Add survey answers to your model training data"""
        conn = sqlite3.connect('political_predictor.db')
        c = conn.cursor()
        c.execute('''INSERT INTO survey_answers 
                     (question_id, user_id, answer, timestamp)
                     VALUES (?, ?, ?, ?)''',
                     (question_id, user_id, answer, datetime.now()))
        conn.commit()
        conn.close()

# 4. Example Usage
if __name__ == "__main__":
    system = PoliticalPredictor()
    
    # User answers survey questions
    system.answer_survey("user123", "q456", "Strongly agree")
    system.answer_survey("user123", "q789", "Education is important")
    
    # User votes on a bill
    bill_id = "C-21"
    print(f"Current prediction for {bill_id}: {system.get_bill_prediction(bill_id)}")
    
    if system.vote_on_bill("user123", bill_id, "for", 3):
        print("Vote successful! Tokens spent.")
        print(f"New prediction: {system.get_bill_prediction(bill_id)}")
    else:
        print("Failed to vote - not enough tokens")
    
    # Export data for model training
    conn = sqlite3.connect('political_predictor.db')
    survey_data = pd.read_sql('''SELECT * FROM survey_answers''', conn)
    vote_data = pd.read_sql('''SELECT * FROM votes''', conn)
    conn.close()
