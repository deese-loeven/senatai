import psycopg2
import os
from datetime import date, datetime # <-- ADDED datetime
import random 

# Import the generation logic from your existing file
from question_generator import generate_questions_for_bill

# Import reward logic
from policap_rewards import award_question_policap

# Utility function (Assuming your connection logic is configured like this)
def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    # Ensure POSTGRES_DB is set, default to 'openparliament' as shown in psql output
    db_name = os.environ.get('POSTGRES_DB', 'openparliament')
    db_user = os.environ.get('POSTGRES_USER', 'dan') # Default to 'dan' as shown in psql output
    
    # You will need to set the POSTGRES_PASSWORD environment variable if it's required
    db_password = os.environ.get('POSTGRES_PASSWORD', 'senatai2025') 
    
    try:
        conn = psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=os.environ.get('POSTGRES_HOST', 'localhost'),
            port=os.environ.get('POSTGRES_PORT', '5432')
        )
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        # Re-raise the error to be caught by the Flask application
        raise

def get_questions_for_user_and_bill(senatair_id, bill_id, num_questions=10):
    """
    Retrieves questions for a bill that the user has NOT answered in the last 30 days.
    If fewer than num_questions are available, it will fill the rest with random questions
    that the user has answered, prioritizing older responses.
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # 1. Get questions the user has NOT answered recently (last 30 days)
        cursor.execute("""
            SELECT q.id, q.question_text, q.question_type, q.bill_id
            FROM questions q
            WHERE q.bill_id = %s
            AND q.id NOT IN (
                SELECT qr.question_id
                FROM question_responses qr
                WHERE qr.user_id = %s
                AND qr.timestamp >= NOW() - INTERVAL '30 days'
            )
            ORDER BY q.created_at DESC -- Prefer newer, unanswered questions
            LIMIT %s
        """, (bill_id, senatair_id, num_questions))
        
        unanswered_questions = cursor.fetchall()
        
        if len(unanswered_questions) >= num_questions:
            return unanswered_questions
            
        # 2. If we need more questions, get questions the user HAS answered, prioritizing oldest responses
        questions_needed = num_questions - len(unanswered_questions)
        
        cursor.execute("""
            SELECT q.id, q.question_text, q.question_type, q.bill_id
            FROM questions q
            JOIN question_responses qr ON q.id = qr.question_id
            WHERE q.bill_id = %s
            AND qr.user_id = %s
            ORDER BY qr.timestamp ASC -- Prefer oldest responses to maximize time between repetitions
            LIMIT %s
        """, (bill_id, senatair_id, questions_needed))
        
        recycled_questions = cursor.fetchall()

        # Combine, ensure no duplicates (shouldn't happen with the logic, but for safety)
        combined_questions = unanswered_questions + [
            q for q in recycled_questions if q['id'] not in [u['id'] for u in unanswered_questions]
        ]
        
        # Shuffle the final list to mix new and old questions
        random.shuffle(combined_questions)

        return combined_questions

    except Exception as e:
        print(f"Database error in get_questions_for_user_and_bill: {e}")
        return []
        
    finally:
        conn.close()

def save_questions_for_bill(bill_id, bill_title, bill_summary, category):
    """
    Generates questions and saves them to the 'questions' table.
    Returns the list of saved questions including their new database IDs.
    """
    questions_data = generate_questions_for_bill(bill_id, bill_title, bill_summary, category)
    conn = None
    saved_questions = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for q in questions_data:
            cursor.execute(
                """
                INSERT INTO questions (bill_id, question_type, question_text, question_options, module_name)
                VALUES (%s, %s, %s, %s, %s) RETURNING id;
                """,
                (bill_id, q.get('type'), q.get('text'), q.get('options'), q.get('module_name'))
            )
            q_id = cursor.fetchone()[0]
            q['id'] = q_id  # Inject the new database ID
            saved_questions.append(q)
            
        conn.commit()
        return saved_questions
        
    except Exception as e:
        print(f"Error saving questions for bill {bill_id}: {e}")
        if conn: conn.rollback()
        return questions_data 
        
    finally:
        if conn: conn.close()
def save_questions_for_bill(bill_id, bill_title, bill_summary, category):
    """
    Generates questions and saves them to the 'questions' table.
    Returns the list of saved questions including their new database IDs.
    """

    # 1. Capture the two lists returned by the new question_generator logic
    permanent_questions, bill_specific_questions = generate_questions_for_bill(bill_id, bill_title, bill_summary, category)
    
    # Combine them for saving
    questions_to_save = permanent_questions + bill_specific_questions
    
    conn = None
    saved_questions = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for q in questions_to_save: # Iterate over the combined list
            cursor.execute(
                """
                -- CRITICAL: Added 'question_hash' to the INSERT
                INSERT INTO questions (bill_id, question_type, question_text, question_options, module_name, question_hash)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
                """,
                # CRITICAL: Added q.get('question_hash') to the parameter tuple
                (bill_id, q.get('type'), q.get('text'), q.get('options'), q.get('module_name'), q.get('question_hash'))
            )
            q_id = cursor.fetchone()[0]
            q['id'] = q_id  # Inject the new database ID
            saved_questions.append(q)
            
        conn.commit()
        return saved_questions
        
    except Exception as e:
        print(f"Error saving questions for bill {bill_id}: {e}")
        if conn: conn.rollback()
        return questions_to_save # Return the generated data even if save fails
        
    finally:
        if conn: conn.close()
def save_question_responses(senatair_id, question_responses):
    """
    Saves the senatair's question responses to the 'question_responses' table and awards Policap.
    """
    conn = None
    total_reward = 0.0
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for name, response in question_responses.items():
            # Name format: 'q_{{ q_id }}_{{ bill.bill_id }}'
            parts = name.split('_')
            if len(parts) != 3 or parts[0] != 'q':
                continue # Skip non-question fields
            
            question_id = parts[1]
            bill_id = parts[2]
            
            response_clean = str(response).strip()
            # Attempt to extract numeric value from response
            numeric_value = None
            try:
                numeric_value = float(response_clean)
            except ValueError:
                pass # Not a numeric response
            
            cursor.execute(
                """
                INSERT INTO question_responses (senatair_id, question_id, bill_id, response_value, response_numeric)
                VALUES (%s, %s, %s, %s, %s);
                """,
                (senatair_id, question_id, bill_id, response_clean, numeric_value)
            )
            
            # Award Policap for this response (using your existing logic)
            reward = award_question_policap(cursor, senatair_id, is_postgres=True)
            total_reward += reward
            
        conn.commit()
        return True, total_reward
        
    except Exception as e:
        print(f"Error saving question responses for senatair {senatair_id}: {e}")
        if conn: conn.rollback()
        return False, 0.0
        
    finally:
        if conn: conn.close()
