import sqlite3
from datetime import datetime

class VoteAuditor:
    def __init__(self, db_path='mydatabase.db'):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        self.cursor = self.conn.cursor()
        self.current_user = None
        self.max_policap_per_vote = 2  # Maximum policaps that can be spent per vote

    def get_user(self):
        """Authenticate or register user and load their policap balance"""
        while True:
            user_id = input("Enter your user ID: ").strip()
            if not 3 <= len(user_id) <= 30:
                print("User ID must be 3-30 characters")
                continue

            self.cursor.execute(
                "SELECT username, tokens FROM Users WHERE user_id = ?",
                (user_id,)
            )
            user = self.cursor.fetchone()

            if user:
                print(f"Welcome back, {user['username']}!")
                self.current_user = {
                    'id': user_id,
                    'username': user['username'],
                    'policaps': user['tokens']
                }
                return True
            else:
                print("User not found. Creating new account...")
                username = input("Enter your display name: ").strip()
                email = input("Enter your email (optional): ").strip() or None
                
                try:
                    self.cursor.execute(
                        """INSERT INTO Users 
                        (user_id, username, email, tokens) 
                        VALUES (?, ?, ?, ?)""",
                        (user_id, username, email, 10.0)  # Starting with 10 policaps
                    )
                    self.conn.commit()
                    print(f"Account created! You've been given 10 starting policaps.")
                    self.current_user = {
                        'id': user_id,
                        'username': username,
                        'policaps': 10.0
                    }
                    return True
                except sqlite3.IntegrityError:
                    print("That user ID or username already exists. Try again.")
                    continue

    def get_bills_with_predictions(self):
        """Retrieve all bills with their predictions"""
        self.cursor.execute("""
            SELECT b.bill_id, b.bill_number, b.bill_title,
                   p.prediction_id, p.predicted_vote, p.predictor_name,
                   COUNT(CASE WHEN a.audit_action = 'affirmed' THEN 1 END) as affirmations,
                   COUNT(CASE WHEN a.audit_action = 'disputed' THEN 1 END) as disputes
            FROM Bills b
            JOIN Predictions p ON b.bill_id = p.bill_id
            LEFT JOIN Audits a ON p.prediction_id = a.prediction_id
            GROUP BY p.prediction_id
            ORDER BY b.bill_number
        """)
        return self.cursor.fetchall()

    def display_bill(self, bill):
        """Format and display a bill with its prediction"""
        print(f"\nBill: {bill['bill_number']} - {bill['bill_title']}")
        print(f"Predicted: {bill['predicted_vote']} (by {bill['predictor_name']})")
        print(f"Community Feedback: 👍 {bill['affirmations']} | 👎 {bill['disputes']}")
        print(f"Your policap balance: {self.current_user['policaps']:.1f}")

    def get_user_decision(self):
        """Get and validate user's decision on a prediction"""
        while True:
            decision = input(
                "\nDo you (a)gree, (d)isagree, or (s)kip? "
                "(1-2 policaps to vote): ").lower()
            
            if decision in ('a', 'd', 's'):
                return decision
            print("Please enter 'a', 'd', or 's'")

    def get_policap_investment(self):
        """Get and validate policap investment amount"""
        while True:
            try:
                amount = float(input(
                    f"How many policaps to invest? (1-{self.max_policap_per_vote}, "
                    f"max {self.current_user['policaps']:.1f}): "))
                
                if (1 <= amount <= self.max_policap_per_vote and 
                    amount <= self.current_user['policaps']):
                    return amount
                print("Invalid amount. Try again.")
            except ValueError:
                print("Please enter a number.")

    def process_audit(self, prediction_id, decision, amount):
        """Record the user's audit decision"""
        action = 'affirmed' if decision == 'a' else 'disputed'
        token = f"audit_{datetime.now().timestamp()}"
        
        try:
            # Record the audit
            self.cursor.execute(
                """INSERT INTO Audits 
                (prediction_id, user_id, audit_action, token) 
                VALUES (?, ?, ?, ?)""",
                (prediction_id, self.current_user['id'], action, token)
            )
            
            # Deduct policaps
            new_balance = self.current_user['policaps'] - amount
            self.cursor.execute(
                "UPDATE Users SET tokens = ? WHERE user_id = ?",
                (new_balance, self.current_user['id'])
            )
            
            self.conn.commit()
            self.current_user['policaps'] = new_balance
            print(f"Success! {amount} policap(s) invested. New balance: {new_balance:.1f}")
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            self.conn.rollback()
            return False

    def audit_predictions(self):
        """Main auditing interface"""
        bills = self.get_bills_with_predictions()
        
        if not bills:
            print("\nNo bills with predictions found in database.")
            return
        
        print("\nVOTE PREDICTION AUDITOR")
        print("=" * 50)
        print(f"Welcome, {self.current_user['username']}")
        print(f"Starting policap balance: {self.current_user['policaps']:.1f}")
        print(f"Each vote costs 1-{self.max_policap_per_vote} policaps\n")
        
        for bill in bills:
            self.display_bill(bill)
            
            decision = self.get_user_decision()
            if decision == 's':
                continue
                
            amount = self.get_policap_investment()
            self.process_audit(bill['prediction_id'], decision, amount)
            
            if self.current_user['policaps'] < 1:
                print("\nYou've run out of policaps!")
# (Keep all your existing class code above this)
if __name__ == "__main__":
    auditor = VoteAuditor()  # Create an instance of the class
    logged_in= False #flag to track login status
    try:
        if auditor.get_user():  # Try to log the user in
           auditor.audit_predictions() # If login successful, start the auditing process
        else:
                print("Exiting.") # Optional: message if login fails entirely
                auditor.conn.close() # Good practice: close the database connection when done
                print("Auditing session finished.")
    except Exception as e:
        print(f"An error occurred: {e}") # Catch potential errors during execution
    finally:
        # Ensure connection is closed regardless of success or error
        if auditor and auditor.conn:
             auditor.conn.close()
             print("Database connection closed.")
        if logged_in:
            print("Auditing session finished.") # Print this only if they logged in
