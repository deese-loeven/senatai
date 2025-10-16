# personalized_predictor3.py
import psycopg2
from collections import defaultdict
import random

class PersonalizedPredictor:
    def __init__(self, user_id):
        self.user_id = user_id
        self.db_conn = psycopg2.connect(
            dbname="openparliament",
            user="dan", 
            password="senatai2025",
            host="localhost"
        )
        # Store user's average sentiment for each keyword: {'keyword': [count, total_score]}
        self.keyword_sentiment = defaultdict(lambda: [0, 0])
        self.load_user_data()

    def load_user_data(self):
        """Loads all past responses for the user to train the simple predictor."""
        print(f"🔄 Loading past responses for User ID: {self.user_id}...")
        cursor = self.db_conn.cursor()
        
        # NOTE: We fetch matched_keywords and the answer_text (the numeric score 1-5)
        cursor.execute("""
            SELECT matched_keywords, answer_text
            FROM senatair_responses
            WHERE senatair_id = %s
            AND answer_text IN ('1', '2', '3', '4', '5')
        """, (self.user_id,))
        
        results = cursor.fetchall()
        
        for keywords_str, score_str in results:
            try:
                score = int(score_str)
                # Keywords are stored as a comma-space separated string: "cost, living, high, ..."
                keywords = [k.strip() for k in keywords_str.split(',')]
                
                for keyword in keywords:
                    if keyword:
                        self.keyword_sentiment[keyword][0] += 1  # Increment count
                        self.keyword_sentiment[keyword][1] += score # Add score
            except ValueError:
                # Skip invalid score_str just in case
                continue

        cursor.close()
        print(f"✅ Loaded {len(results)} responses. Analyzed {len(self.keyword_sentiment)} unique keywords.")

    def calculate_average_sentiments(self):
        """Calculates the weighted average score for each keyword."""
        final_sentiments = {}
        for keyword, (count, total) in self.keyword_sentiment.items():
            if count >= 1: # Require at least 1 response to form a valid average
                average = total / count
                final_sentiments[keyword] = average
        return final_sentiments

    def predict_bill_stance(self, bill_keywords, final_sentiments):
        """
        Predicts the user's stance on a new bill based on its matching keywords.
        Prediction is the weighted average of the user's past keyword sentiments.
        """
        total_score = 0
        total_weight = 0
        
        for keyword in bill_keywords:
            if keyword in final_sentiments:
                # Weight the score by the number of times we've seen this keyword (count)
                # This ensures well-tested keywords have a stronger influence
                count = self.keyword_sentiment[keyword][0]
                sentiment = final_sentiments[keyword]
                
                total_score += sentiment * count
                total_weight += count

        if total_weight == 0:
            # If no keywords match our trained data, use a neutral prediction (3.0)
            return 3.0, "Neutral (No prior matching sentiment data)"

        # The prediction is the overall weighted average sentiment
        prediction_score = total_score / total_weight
        
        # Convert the numeric score back to a user-friendly prediction
        if prediction_score < 2.5:
            stance = "Likely Oppose"
        elif prediction_score < 3.5:
            stance = "Neutral/Uncertain"
        else:
            stance = "Likely Support"
            
        return prediction_score, stance

    def run_prediction_demo(self):
        """Runs a demonstration of the prediction model."""
        
        final_sentiments = self.calculate_average_sentiments()
        
        print("\n--- Current User Sentiment Profile (Top 5) ---")
        # Sort and display the most frequent (most reliable) sentiments
        sorted_sentiments = sorted(final_sentiments.items(), key=lambda item: self.keyword_sentiment[item[0]][0], reverse=True)
        
        for keyword, score in sorted_sentiments[:5]:
            count = self.keyword_sentiment[keyword][0]
            print(f"📊 '{keyword}': Avg Score {score:.2f} ({count} responses)")
        
        print("\n-------------------------------------------")
        print("🧠 Predicting User Stance on an UNSEEN Bill...")
        
        # --- DEMO CASE 1: Bill matching user's keywords ---
        # Keywords used in your last survey: ['cost', 'living', 'high', 'immigration', 'destabilizing', 'canadian', 'medium', 'literacy']
        test_bill_keywords = ['cost', 'living', 'housing', 'interest', 'canadian'] 
        
        pred_score, pred_stance = self.predict_bill_stance(test_bill_keywords, final_sentiments)
        
        print("\n--- DEMO 1: Cost of Living Bill ---")
        print(f"Keywords: {', '.join(test_bill_keywords)}")
        print(f"PREDICTION: {pred_stance} (Score: {pred_score:.2f} on 1-5 scale)")
        
        # --- DEMO CASE 2: Bill with neutral or unrelated keywords ---
        test_bill_keywords_2 = ['telecom', 'infrastructure', 'bandwidth', 'regulation']
        
        pred_score_2, pred_stance_2 = self.predict_bill_stance(test_bill_keywords_2, final_sentiments)

        print("\n--- DEMO 2: Neutral Telecom Bill ---")
        print(f"Keywords: {', '.join(test_bill_keywords_2)}")
        print(f"PREDICTION: {pred_stance_2} (Score: {pred_score_2:.2f} on 1-5 scale)")


    def __del__(self):
        """Ensure the database connection is closed."""
        if self.db_conn:
            self.db_conn.close()

if __name__ == "__main__":
    # Use the Test User ID you've been using
    predictor = PersonalizedPredictor(user_id=1) 
    predictor.run_prediction_demo()
