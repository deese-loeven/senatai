import sqlite3
from datetime import datetime

class VotePredictor:
    def __init__(self, db_name="survey_data.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self):
        # Drop the existing predicted_votes table (if you're okay with losing data)
        self.cursor.execute('DROP TABLE IF EXISTS predicted_votes')
        # Recreate predicted_votes with the correct schema
        self.cursor.execute('''
            CREATE TABLE predicted_votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_text TEXT,
                user_id TEXT,
                predictor_model TEXT,
                predicted_vote TEXT,
                final_vote TEXT,
                explanation TEXT,
                priority INTEGER DEFAULT 1,
                timestamp DATETIME
            )
        ''')
        # Ensure predictor_ratings table exists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictor_ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                predictor_model TEXT,
                rating INTEGER,
                timestamp DATETIME
            )
        ''')
        self.conn.commit()
        print("Prediction database initialized successfully!")

    def get_user_answers(self, user_id):
        self.cursor.execute("""
            SELECT q.question_text, q.question_type, a.answer, a.score
            FROM answers a
            JOIN questions q ON a.question_id = q.id
            WHERE a.user_id = ?
        """, (user_id,))
        answer_rows = self.cursor.fetchall()
        answers = []
        for row in answer_rows:
            question_text, question_type, answer, score = row
            answers.append({
                "question": question_text,
                "type": question_type,
                "answer": answer,
                "score": score
            })
        return answers

    def predict_vote_simple(self, bill_text, user_answers):
        relevant_answers = []
        bill_text_lower = bill_text.lower()
        for answer in user_answers:
            question = answer["question"].lower()
            if any(word in bill_text_lower for word in question.split()):
                relevant_answers.append(answer)

        if not relevant_answers:
            return "neutral", "No relevant answers found."

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
                score = answer["score"]
                if score < 3:
                    total_score -= (3 - score) * 0.5
                elif score > 3:
                    total_score += (score - 3) * 0.5
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

    def predict_vote_alternative(self, bill_text, user_answers):
        positive_count = 0
        total_count = 0
        bill_text_lower = bill_text.lower()
        for answer in user_answers:
            question = answer["question"].lower()
            if any(word in bill_text_lower for word in question.split()):
                total_count += 1
                if answer["type"] == "yes_no" and answer["answer"] == "yes":
                    positive_count += 1
                elif answer["type"] == "scale_1_to_5" and answer["score"] is not None and answer["score"] > 3:
                    positive_count += 1

        if total_count == 0:
            return "neutral", "No relevant answers found."

        if positive_count > 0:
            return "yes", f"Found {positive_count} positive responses out of {total_count} relevant answers."
        else:
            return "no", f"No positive responses found out of {total_count} relevant answers."

    def store_prediction(self, bill_text, user_id, predictor_model, predicted_vote, explanation):
        self.cursor.execute(
            "INSERT INTO predicted_votes (bill_text, user_id, predictor_model, predicted_vote, final_vote, explanation, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (bill_text, user_id, predictor_model, predicted_vote, predicted_vote, explanation, datetime.now())
        )
        self.conn.commit()

    def store_rating(self, user_id, predictor_model, rating):
        self.cursor.execute(
            "INSERT INTO predictor_ratings (user_id, predictor_model, rating, timestamp) VALUES (?, ?, ?, ?)",
            (user_id, predictor_model, rating, datetime.now())
        )
        self.conn.commit()

    def run_prediction(self, user_id, predictor_model):
        legislation = [
            "Increase funding for education programs",
            "Raise taxes to support healthcare",
            "Promote clean energy initiatives",
            "Restrict digital privacy regulations",
            "Support small business tax breaks"
        ]

        user_answers = self.get_user_answers(user_id)
        if not user_answers:
            print("No answers found. Please complete some surveys first.")
            return False

        if predictor_model == "simple":
            predict_func = self.predict_vote_simple
        elif predictor_model == "alternative":
            predict_func = self.predict_vote_alternative
        else:
            print("Invalid predictor model selected.")
            return False

        for bill in legislation:
            predicted_vote, explanation = predict_func(bill, user_answers)
            self.store_prediction(bill, user_id, predictor_model, predicted_vote, explanation)

        print(f"Predictions made using {predictor_model} model and stored in database.")
        return True

def main():
    user_id = "user123"
    predictor = VotePredictor()

    models = ["simple", "alternative"]
    print("Available predictor models:")
    for i, model in enumerate(models, 1):
        print(f"{i}. {model}")

    choice = input("Choose a predictor model (1-2): ")
    try:
        choice = int(choice)
        if 1 <= choice <= len(models):
            selected_model = models[choice - 1]
        else:
            print("Invalid choice. Using default 'simple' model.")
            selected_model = "simple"
    except ValueError:
        print("Invalid input. Using default 'simple' model.")
        selected_model = "simple"

    success = predictor.run_prediction(user_id, selected_model)
    if not success:
        return

    rating = input(f"Rate the '{selected_model}' predictor model (1-5, 1=poor, 5=excellent): ")
    try:
        rating = int(rating)
        if 1 <= rating <= 5:
            predictor.store_rating(user_id, selected_model, rating)
            print(f"Rating of {rating} stored for {selected_model} model.")
        else:
            print("Rating must be between 1 and 5. Rating not stored.")
    except ValueError:
        print("Invalid input. Rating not stored.")

if __name__ == "__main__":
    main()
