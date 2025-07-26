import sqlite3
import re
from datetime import datetime

def initialize_prediction_database(db_name="survey_data.db"):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predicted_votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_text TEXT,
                user_id TEXT,
                predicted_vote TEXT,
                explanation TEXT,
                timestamp DATETIME
            )
        ''')
        conn.commit()
        conn.close()
        print("Prediction database initialized successfully!")
    except Exception as e:
        print(f"Error initializing prediction database: {e}")

def get_user_answers(user_id, db_name="survey_data.db"):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Retrieve user answers with their questions and types
        cursor.execute("""
            SELECT q.question_text, q.question_type, a.answer, a.score
            FROM answers a
            JOIN questions q ON a.question_id = q.id
            WHERE a.user_id = ?
        """, (user_id,))
        answer_rows = cursor.fetchall()
        answers = []
        for row in answer_rows:
            question_text, question_type, answer, score = row
            answers.append({
                "question": question_text,
                "type": question_type,
                "answer": answer,
                "score": score
            })

        conn.close()
        return answers

    except Exception as e:
        print(f"Error retrieving user answers: {e}")
        return []

def predict_vote(bill_text, user_answers):
    # Simple prediction: look for keywords in bill text and match to user answers
    relevant_answers = []
    bill_text_lower = bill_text.lower()

    for answer in user_answers:
        question = answer["question"].lower()
        # Check if the bill text contains keywords from the question
        if any(word in bill_text_lower for word in question.split()):
            relevant_answers.append(answer)

    if not relevant_answers:
        return "neutral", "No relevant answers found."

    # Score the bill based on user answers
    total_score = 0
    count = 0
    for answer in relevant_answers:
        if answer["type"] == "yes_no":
            if answer["answer"] == "yes":
                total_score += 1
            elif answer["answer"] == "no":
                total_score -= 1
            count += 1
        elif answer["type"] == "scale_1_to_5" and answer["score"] is not None:
            # Map 1-5 scale to -1 to 1
            # 1,2 -> negative; 3 -> neutral; 4,5 -> positive
            score = answer["score"]
            if score < 3:
                total_score -= (3 - score) * 0.5  # 1=-1, 2=-0.5
            elif score > 3:
                total_score += (score - 3) * 0.5  # 4=0.5, 5=1
            count += 1

    if count == 0:
        return "neutral", "No relevant answers with usable responses."

    avg_score = total_score / count
    if avg_score > 0:
        return "yes", f"Average score {avg_score:.2f} (positive) based on {count} relevant answers."
    elif avg_score < 0:
        return "no", f"Average score {avg_score:.2f} (negative) based on {count} relevant answers."
    else:
        return "neutral", f"Average score {avg_score:.2f} (neutral) based on {count} relevant answers."

def store_prediction(bill_text, user_id, predicted_vote, explanation, db_name="survey_data.db"):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO predicted_votes (bill_text, user_id, predicted_vote, explanation, timestamp) VALUES (?, ?, ?, ?, ?)",
            (bill_text, user_id, predicted_vote, explanation, datetime.now())
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error storing prediction: {e}")

def get_policap_balance(user_id, db_name="survey_data.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT tokens FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def spend_policap(user_id, amount, db_name="survey_data.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET tokens = tokens - ? WHERE id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def main():
    user_id = "user123"
    initialize_prediction_database()

    # Mock legislation (replace with scraper data later)
    legislation = [
        "Increase funding for education programs",
        "Raise taxes to support healthcare",
        "Promote clean energy initiatives",
        "Restrict digital privacy regulations",
        "Support small business tax breaks"
    ]

    # Get user answers
    user_answers = get_user_answers(user_id)
    if not user_answers:
        print("No user answers found. Please complete some surveys first.")
        return

    # Check policap balance
    policap_balance = get_policap_balance(user_id)
    print(f"Your policap balance: {policap_balance}")

    # Let user choose to vote directly or delegate
    for bill in legislation:
        print(f"\nBill: {bill}")
        if policap_balance >= 10:
            choice = input("Spend 10 policap to vote directly? (yes/no): ").lower()
            if choice == "yes":
                vote = input("Your vote (yes/no): ").lower()
                spend_policap(user_id, 10)
                policap_balance -= 10
                explanation = "User voted directly."
                print(f"You voted: {vote}")
            else:
                predicted_vote, explanation = predict_vote(bill, user_answers)
                print(f"Predicted Vote: {predicted_vote}")
                print(f"Explanation: {explanation}")
                vote = predicted_vote
        else:
            predicted_vote, explanation = predict_vote(bill, user_answers)
            print(f"Predicted Vote: {predicted_vote}")
            print(f"Explanation: {explanation}")
            vote = predicted_vote

        store_prediction(bill, user_id, vote, explanation)
        print(f"Policap balance remaining: {policap_balance}")

if __name__ == "__main__":
    main()
