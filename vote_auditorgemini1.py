import sqlite3
from datetime import datetime

class VoteAuditor:
    def __init__(self, db_path="senatai.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def get_all_bills(self):
        self.cursor.execute("SELECT DISTINCT bill_text FROM predicted_votes")
        return [row[0] for row in self.cursor.fetchall()]

    def get_predictions_for_bill(self, bill_text):
        self.cursor.execute("""
            SELECT Senatair_id, model_name, predicted_vote, explanation, timestamp
            FROM predicted_votes
            WHERE bill_text = ?
        """, (bill_text,))
        return self.cursor.fetchall()

    def record_feedback(self, bill_text, Senatair_id, model_name, predicted_vote, agreement, policap_yes, policap_no):
        self.cursor.execute("""
            INSERT INTO prediction_feedback (bill_text, Senatair_id, model_name, predicted_vote, user_agreement, policap_spent_yes, policap_spent_no)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (bill_text, Senatair_id, model_name, predicted_vote, agreement, policap_yes, policap_no))
        self.conn.commit()

    def get_user_policap(self, Senatair_id):
        self.cursor.execute("SELECT policap FROM Senatairs WHERE Senatair_id = ?", (Senatair_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0.0

    def update_user_policap(self, Senatair_id, policap):
        self.cursor.execute("UPDATE Senatairs SET policap = ? WHERE Senatair_id = ?", (policap, Senatair_id))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()

def main():
    auditor = VoteAuditor()

    bills = auditor.get_all_bills()

    print("Available Bills:")
    for i, bill in enumerate(bills):
        print(f"{i + 1}. {bill}")

    bill_choice = int(input("Select a bill (1-{}): ".format(len(bills)))) - 1
    selected_bill = bills[bill_choice]

    predictions = auditor.get_predictions_for_bill(selected_bill)

    print("\nPredictions for Bill:")
    for Senatair_id, model_name, predicted_vote, explanation, timestamp in predictions:
        print(f"User: {Senatair_id}")
        print(f"Model: {model_name}")
        print(f"Predicted: {predicted_vote}")
        print(f"Explanation: {explanation}")
        print(f"Timestamp: {timestamp}")

        agreement = input("Do you agree with this prediction? (yes/no/neutral): ").lower()
        policap_yes = 0
        policap_no = 0

        if agreement in ['yes','no']:
            policap_yes = int(input("Policap to spend on yes (0-2): "))
            policap_no = int(input("Policap to spend on no (0-2): "))

            user_policap = auditor.get_user_policap(Senatair_id)
            if policap_yes + policap_no <= 2 and policap_yes + policap_no <= user_policap:
                auditor.record_feedback(selected_bill, Senatair_id, model_name, predicted_vote, agreement, policap_yes, policap_no)
                auditor.update_user_policap(Senatair_id, user_policap - (policap_yes + policap_no))
                print("Feedback recorded and policap updated.")
            else:
                print("Invalid policap spending or insufficient funds.")
        else:
            auditor.record_feedback(selected_bill, Senatair_id, model_name, predicted_vote, agreement, 0, 0)
            print('feedback recorded.')
    auditor.close_connection()

if __name__ == "__main__":
    main()
