#!/usr/bin/env python3
import sqlite3
from datetime import datetime

class VotePredictor:
    def __init__(self, db_name="survey_data.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self):
        """Ensure required tables exist"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS predicted_votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_text TEXT,
                user_id TEXT,
                predictor_model TEXT,
                predicted_vote TEXT,
                confidence REAL,
                explanation TEXT,
                timestamp DATETIME
            )
        ''')
        self.conn.commit()

    def predict_vote(self, user_id, bill_text, model="simple"):
        """
        Predicts how a user would vote on a bill
        Returns: (predicted_vote, confidence, explanation)
        """
        user_answers = self._get_user_answers(user_id)
        
        if model == "simple":
            return self._simple_model(bill_text, user_answers)
        elif model == "alternative":
            return self._alternative_model(bill_text, user_answers)
        else:
            raise ValueError(f"Unknown model: {model}")

    def _get_user_answers(self, user_id):
        """Retrieve user's past answers from database"""
        self.cursor.execute("""
            SELECT q.question_text, q.question_type, a.answer, a.score 
            FROM answers a
            JOIN questions q ON a.question_id = q.id
            WHERE a.user_id = ?
        """, (user_id,))
        return [{
            'question': row[0],
            'type': row[1],
            'answer': row[2],
            'score': row[3]
        } for row in self.cursor.fetchall()]

    def _simple_model(self, bill_text, user_answers):
        """
        Basic prediction model:
        - Looks for keywords from past questions in the bill text
        - Scores based on past answers
        """
        relevant_answers = []
        bill_keywords = set(bill_text.lower().split())
        
        for answer in user_answers:
            question_keywords = set(answer['question'].lower().split())
            if bill_keywords & question_keywords:  # Any overlap
                relevant_answers.append(answer)

        if not relevant_answers:
            return "neutral", 0.5, "No relevant voting history found"

        total_score = 0
        for answer in relevant_answers:
            if answer['type'] == 'yes_no':
                total_score += 1 if answer['answer'] == 'yes' else -1
            elif answer['type'] == 'scale_1_to_5' and answer['score']:
                total_score += (answer['score'] - 3) * 0.5  # Convert 1-5 to -1 to +1 range

        avg_score = total_score / len(relevant_answers)
        confidence = min(0.99, abs(avg_score))  # 0-0.99 range
        
        if avg_score > 0.1:
            return "yes", confidence, f"{len(relevant_answers)} relevant votes, mostly positive"
        elif avg_score < -0.1:
            return "no", confidence, f"{len(relevant_answers)} relevant votes, mostly negative"
        else:
            return "neutral", 0.5, f"{len(relevant_answers)} relevant votes, no clear trend"

    def _alternative_model(self, bill_text, user_answers):
        """
        Alternative model:
        - More strict keyword matching
        - Only counts clear positive/negative responses
        """
        positive = 0
        negative = 0
        bill_keywords = set(bill_text.lower().split())
        
        for answer in user_answers:
            question_keywords = set(answer['question'].lower().split())
            shared_keywords = bill_keywords & question_keywords
            if len(shared_keywords) >= 2:  # Requires at least 2 matching keywords
                if answer['type'] == 'yes_no':
                    if answer['answer'] == 'yes': positive += 1
                    else: negative += 1
                elif answer['type'] == 'scale_1_to_5' and answer['score']:
                    if answer['score'] > 3: positive += 1
                    elif answer['score'] < 3: negative += 1

        total = positive + negative
        if total == 0:
            return "neutral", 0.5, "No strong opinions detected"
        
        confidence = min(0.99, max(positive, negative) / total)
        if positive > negative:
            return "yes", confidence, f"{positive} clear positive votes out of {total}"
        elif negative > positive:
            return "no", confidence, f"{negative} clear negative votes out of {total}"
        else:
            return "neutral", 0.5, f"Split decision: {positive} yes, {negative} no"

    def save_prediction(self, user_id, bill_text, model, vote, confidence, explanation):
        """Store prediction in database"""
        self.cursor.execute("""
            INSERT INTO predicted_votes 
            (bill_text, user_id, predictor_model, predicted_vote, confidence, explanation, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (bill_text, user_id, model, vote, confidence, explanation, datetime.now()))
        self.conn.commit()

    def close(self):
        """Clean up database connection"""
        self.conn.close()

if __name__ == "__main__":
    # Example usage
    predictor = VotePredictor()
    
    # Sample prediction - replace with real user ID from your database
    user = "user123"
    bill = "Increase funding for public schools"
    
    print("\nSimple Model Prediction:")
    vote, confidence, explanation = predictor.predict_vote(user, bill, "simple")
    print(f"Bill: {bill}")
    print(f"Predicted vote: {vote} (Confidence: {confidence:.0%})")
    print(f"Reason: {explanation}")
    predictor.save_prediction(user, bill, "simple", vote, confidence, explanation)
    
    print("\nAlternative Model Prediction:")
    vote, confidence, explanation = predictor.predict_vote(user, bill, "alternative")
    print(f"Bill: {bill}")
    print(f"Predicted vote: {vote} (Confidence: {confidence:.0%})")
    print(f"Reason: {explanation}")
    predictor.save_prediction(user, bill, "alternative", vote, confidence, explanation)
    
    predictor.close()
