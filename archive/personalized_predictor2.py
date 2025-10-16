# personalized_predictor.py
import psycopg2
from typing import List, Dict, Any, Tuple
import time

# --- Configuration (Copied from adaptive_survey8.py for integration) ---
DB_NAME = "openparliament"
DB_USER = "dan"
DB_PASS = "senatai2025"
DB_HOST = "localhost"

# NOTE: In a real system, the NEW_LAW theme/keywords would come from the legislative scraper/processor
NEW_LAW_TO_PREDICT = {
    "title": "Clean Water Infrastructure Bill (H-301)",
    "bill_number": "H-301",
    "required_keywords": ["water", "infrastructure", "funding", "environmental"] # Keywords this law addresses
}

# --- Core Vote Prediction Logic ---

class PersonalizedPredictor:
    def __init__(self):
        self.db_conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST
        )
        # Placeholder URL for the wiki explanation
        self.wiki_link = "http://senatai.coop/wiki/personalized_theme_v10_match"

    def __del__(self):
        """Ensure connection is closed on cleanup."""
        if self.db_conn:
            self.db_conn.close()

    def fetch_relevant_answers(self, senatair_id: int, law_keywords: List[str]) -> List[Tuple[str, str, str]]:
        """
        Fetches a Senatair's past responses where the stored keywords overlap
        with the current law's keywords.
        """
        keywords_sql = [kw.strip() for kw in law_keywords]
        
        # We fetch all responses and filter the keyword match in Python for now, 
        # as the 'matched_keywords' column is a text string of comma-separated values.
        cursor = self.db_conn.cursor()
        cursor.execute("""
            SELECT question_text, answer_text, matched_keywords 
            FROM senatair_responses 
            WHERE senatair_id = %s;
        """, (senatair_id,))
        
        raw_answers = cursor.fetchall()
        cursor.close()

        relevant_answers = []
        for question_text, answer_score_str, matched_keywords_str in raw_answers:
            
            # 1. Check for keyword relevance (Intersection between law keywords and user's past interest)
            past_kws = [kw.strip() for kw in matched_keywords_str.lower().split(',')]
            
            # Simple check: Is there *any* overlap in keywords?
            if any(kw in past_kws for kw in keywords_sql):
                try:
                    score = int(answer_score_str)
                    if 1 <= score <= 5:
                        relevant_answers.append({
                            "question": question_text,
                            "answer_score": score,
                            "matched_keywords": matched_keywords_str
                        })
                except ValueError:
                    # Skip answers that are not the expected 1-5 score
                    continue

        return relevant_answers

    def predict_vote(self, senatair_id: int, law_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predicts a Senatair's vote based on past answers related to the law's keywords.
        """
        
        relevant_answers = self.fetch_relevant_answers(senatair_id, law_data['required_keywords'])
        
        num_answers = len(relevant_answers)
        
        if num_answers == 0:
            return {
                "prediction": "UNDECIDED",
                "confidence": "0%",
                "reasoning_answers": [],
                "method_wiki_link": self.wiki_link
            }

        # 1. Calculate Average Score
        total_score = sum(a['answer_score'] for a in relevant_answers)
        average_score = total_score / num_answers
        
        # 2. Determine Prediction and Confidence
        # Mid-point is 3. Scores > 3 are YES, Scores < 3 are NO.
        if average_score > 3.0:
            prediction = "VOTE YES"
            # Confidence is based on distance from 3.0 midpoint (Max distance is 2)
            confidence_value = abs(average_score - 3.0) / 2.0 
        elif average_score < 3.0:
            prediction = "VOTE NO"
            confidence_value = abs(average_score - 3.0) / 2.0
        else: # Exactly 3.0
            prediction = "UNDECIDED (Neutral)"
            confidence_value = 0.1 # Minimal confidence
            
        confidence_percent = round(min(1.0, confidence_value) * 100) # Cap at 100%
        
        # 3. Compile Reasoning for Transparency
        reasoning_list = [
            {
                "question": a['question'], 
                "score": a['answer_score'], 
                "keywords_matched": a['matched_keywords']
            } 
            for a in relevant_answers
        ]
            
        return {
            "law": law_data['title'],
            "prediction": prediction,
            "confidence": f"{confidence_percent}%",
            "reasoning_answers": reasoning_list,
            "method_wiki_link": self.wiki_link
        }

# --- Execution Example (Mimics the "Audit Predictions" Button) ---
if __name__ == "__main__":
    # NOTE: This assumes Senatair ID 1 exists and has answered questions using the
    # updated adaptive_survey8.py script!
    TEST_USER_ID = 1 
    
    print(f"--- Running Prediction Audit for Senatair ID: {TEST_USER_ID} ---")
    
    try:
        predictor = PersonalizedPredictor()
        
        print(f"\n🔍 Analyzing Senatair {TEST_USER_ID}'s stance on: {NEW_LAW_TO_PREDICT['title']}")
        
        result = predictor.predict_vote(TEST_USER_ID, NEW_LAW_TO_PREDICT)
        
        print("\n**✅ PREDICTION RESULT:**")
        print(f"   Law: {result['law']}")
        print(f"   **Prediction:** {result['prediction']}")
        print(f"   **Confidence:** {result['confidence']}")
        
        print("\n📝 **REASONING FOR ASSESSMENT:**")
        if result['reasoning_answers']:
            for answer in result['reasoning_answers']:
                print(f"   - **Score:** {answer['score']} | **Question:** '{answer['question'][:50]}...'")
                print(f"     *Used Keywords:* {answer['keywords_matched']}")
        else:
            print("   No relevant past answers found in the database to base the prediction on.")

        print(f"\n🌐 **Methodology Hyperlink (Audit Option):**")
        print(f"   [Prediction Method Explained]({result['method_wiki_link']})")
        
    except psycopg2.Error as e:
        print(f"\nFATAL ERROR: Could not connect to PostgreSQL. Please check credentials/service: {e}")
