import sqlite3
import re

def initialize_prediction_database():
    try:
        conn = sqlite3.connect('predictions.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOTORMATION EXISTS predicted_votes (
                bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_text TEXT,
                predicted_vote TEXT,
                explanation TEXT
            )
        ''')
        conn.commit()
        conn.close()
        print("Prediction database initialized successfully!")
    except Exception as e:
        print(f"Error initializing prediction database: {e}")

def get_legislation_and_answers():
    try:
        conn = sqlite3.connect('survey.db')
        cursor = conn.cursor()

        # Retrieve all legislation texts.
        cursor.execute("SELECT DISTINCT question FROM questions WHERE theme != 'unknown'") # get all the questions that have a theme
        legislation_rows = cursor.fetchall()
        legislation = [row[0] for row in legislation_rows]

        # Retrieve user answers.
        cursor.execute("SELECT question, answer FROM questions WHERE answer IS NOT NULL")
        answer_rows = cursor.fetchall()
        answers = {row[0]: row[1] for row in answer_rows}

        conn.close()
        return legislation, answers

    except Exception as e:
        print(f"Error retrieving data: {e}")
        return [], {}

def predict_vote(bill_text, user_answers):
    # Very basic prediction logic (replace with more sophisticated methods)
    relevant_answers = {}
    for question, answer in user_answers.items():
        if re.search(r'\b' + re.escape(question.split('?')[0].lower().split('should')[1].strip()) + r'\b', bill_text.lower()): #checks if the question stems from the bill text
            relevant_answers[question] = answer

    if not relevant_answers:
        return "neutral", "No relevant answers found."

    yes_count = sum(1 for answer in relevant_answers.values() if answer == "yes")
    no_count = sum(1 for answer in relevant_answers.values() if answer == "no")

    if yes_count > no_count:
        return "yes", f"More 'yes' answers ({yes_count}) than 'no' answers ({no_count}) for relevant questions."
    elif no_count > yes_count:
        return "no", f"More 'no' answers ({no_count}) than 'yes' answers ({yes_count}) for relevant questions."
    else:
        return "neutral", "Equal 'yes' and 'no' answers for relevant questions."

def store_prediction(bill_text, predicted_vote, explanation):
    try:
        conn = sqlite3.connect('predictions.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO predicted_votes (bill_text, predicted_vote, explanation) VALUES (?, ?, ?)",
                       (bill_text, predicted_vote, explanation))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error storing prediction: {e}")

def main():
    initialize_prediction_database()
    legislation, user_answers = get_legislation_and_answers()

    for bill in legislation:
        predicted_vote, explanation = predict_vote(bill, user_answers)
        store_prediction(bill, predicted_vote, explanation)
        print(f"Bill: {bill}\nPredicted Vote: {predicted_vote}\nExplanation: {explanation}\n")

if __name__ == "__main__":
    main()
