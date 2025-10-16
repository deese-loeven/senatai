import psycopg2
from typing import List, Dict, Any, Tuple

# --- Configuration (REPLACE WITH YOUR ACTUAL DETAILS) ---
DB_NAME = "openparliament"
DB_USER = "postgres"
DB_PASS = "YOUR_POSTGRES_PASSWORD" # You will need to replace this
DB_HOST = "localhost"

# --- Dummy Data for Testing ---
TEST_SENATAIR_ID = 42 # Use a known Senatair's ID for testing
NEW_LAW_THEME = "economic" # Theme of the law we are predicting a vote on
NEW_LAW_TITLE = "Small Business Tax Relief Act"

# --- Theme-Keyword Mapping (Rudimentary Topic Extraction) ---
# NOTE: In a real system, you would get this data from a dedicated keyword extractor 
# like your 'extract_keywords.py' or 'bill_keywords' table.
THEME_KEYWORDS = {
    "economic": ["tax", "business", "subsidy", "finance", "budget", "cost"],
    "environment": ["carbon", "conservation", "wildlife", "energy", "climate"],
    "rights": ["equality", "protest", "gun", "liberty", "freedom"]
}

# --- Database Interaction Functions ---

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

def fetch_senatair_answers(senatair_id: int) -> List[Tuple[str, str, str]]:
    """
    Fetches a Senatair's past responses from the database.
    (question_text, answer_text, matched_keywords)
    """
    conn = get_db_connection()
    if not conn:
        return []
        
    try:
        cur = conn.cursor()
        # Fetch question_text, answer_text, and matched_keywords
        cur.execute("""
            SELECT question_text, answer_text, matched_keywords 
            FROM senatair_responses 
            WHERE senatair_id = %s;
        """, (senatair_id,))
        
        # The output of this function is a list of tuples: (question, answer, keywords)
        answers = cur.fetchall()
        cur.close()
        conn.close()
        return answers
    except psycopg2.Error as e:
        print(f"Error fetching data: {e}")
        return []

# --- The Core Vote Prediction Logic ---

def predict_vote_personalized(senatair_id: int, law_theme: str, law_title: str) -> Dict[str, Any]:
    """
    Predicts a Senatair's vote based on past answers related to the law's theme.
    """
    # 1. Fetch the real data from the database
    raw_answers = fetch_senatair_answers(senatair_id)
    
    # 2. Process and Filter Answers
    relevant_scores = []
    reasoning_answers = []

    for question_text, answer_text, matched_keywords in raw_answers:
        # A simple model: if the answer contains any of the law's theme keywords, it's relevant.
        # This is a rudimentary proxy for "theme matching."
        is_relevant = any(kw in matched_keywords.lower() for kw in THEME_KEYWORDS.get(law_theme, []))

        if is_relevant:
            try:
                # Assume the answer is a numeric score (e.g., 1-5 scale)
                score = int(answer_text) 
                if 1 <= score <= 5:
                    relevant_scores.append(score)
                    reasoning_answers.append({
                        "question": question_text,
                        "answer": answer_text,
                        "bill_theme": law_theme
                    })
            except ValueError:
                # Ignore non-numeric answers (like Yes/No, which need conversion) for now
                pass 

    # 3. Prediction Calculation
    num_answers = len(relevant_scores)
    
    if num_answers == 0:
        return {
            "law": law_title,
            "prediction": "UNDECIDED (Insufficient Data)",
            "confidence": "0%",
            "reasoning_answers": [],
            "method_wiki_link": "http://senatai.coop/wiki/personalized_theme_v9"
        }
        
    average_score = sum(relevant_scores) / num_answers
    
    # Mid-point is 3. Scores > 3 are YES, Scores < 3 are NO.
    if average_score > 3.0:
        prediction = "VOTE YES"
        confidence_value = abs(average_score - 3.0) / 2.0 
    elif average_score < 3.0:
        prediction = "VOTE NO"
        confidence_value = abs(average_score - 3.0) / 2.0
    else: # Exactly 3.0
        prediction = "UNDECIDED (Neutral)"
        confidence_value = 0.1 # Low confidence for perfect neutrality
        
    confidence_percent = round(confidence_value * 100)
    
    return {
        "law": law_title,
        "prediction": prediction,
        "confidence": f"{confidence_percent}%",
        "reasoning_answers": reasoning_answers,
        "method_wiki_link": "http://senatai.coop/wiki/personalized_theme_v9"
    }

# --- 4. Execution Example ---

if __name__ == "__main__":
    # NOTE: You MUST replace DB_PASS and ensure a Senatair with ID 42 exists 
    # and has answered questions in your 'senatair_responses' table for this to work.
    
    print(f"--- Running Prediction for Senatair ID: {TEST_SENATAIR_ID} on Law: {NEW_LAW_TITLE} ({NEW_LAW_THEME}) ---")
    
    result = predict_vote_personalized(TEST_SENATAIR_ID, NEW_LAW_THEME, NEW_LAW_TITLE)
    
    print("\n✅ PREDICTION RESULT:")
    print(f"   Law: {result['law']}")
    print(f"   **Prediction:** {result['prediction']}")
    print(f"   **Confidence:** {result['confidence']}")
    print(f"   Method Link: {result['method_wiki_link']}")
    
    print("\n📝 REASONING (Answers Used):")
    if result['reasoning_answers']:
        for answer in result['reasoning_answers']:
            # The 'answer' is the raw numeric score, as per your question format
            print(f"   - Q: '{answer['question']}' (Theme: {answer['bill_theme']}) -> Score: {answer['answer']}")
    else:
        print("   No relevant past answers found in the database to base the prediction on.")
