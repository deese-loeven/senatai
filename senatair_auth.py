# senatair_auth.py
import psycopg2
import hashlib
import secrets
from datetime import datetime, date

class SenatairAuth:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="openparliament",
            user="dan",
            password="senatai2025",
            host="localhost"
        )
    
    def create_senatair(self, username, email=None, initial_policaps=25.0):
        """Create a new Senatair user"""
        cur = self.conn.cursor()
        try:
            cur.execute("""
                INSERT INTO senatairs (username, email, policaps)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (username, email, initial_policaps))
            senatair_id = cur.fetchone()[0]
            self.conn.commit()
            print(f"✅ Created new Senatair: {username} (ID: {senatair_id})")
            return senatair_id
        except psycopg2.IntegrityError:
            self.conn.rollback()
            print(f"❌ Username {username} already exists")
            return None
        finally:
            cur.close()
    
    def get_senatair(self, username):
        """Get Senatair by username"""
        cur = self.conn.cursor()
        cur.execute("SELECT id, username, email, policaps, daily_answer_count FROM senatairs WHERE username = %s", (username,))
        result = cur.fetchone()
        cur.close()
        
        if result:
            return {
                'id': result[0],
                'username': result[1],
                'email': result[2],
                'policaps': float(result[3]),
                'daily_answers': result[4]
            }
        return None
    
    def start_session(self, senatair_id):
        """Start a new session for a Senatair"""
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO senatair_sessions (senatair_id) 
            VALUES (%s) 
            RETURNING id
        """, (senatair_id,))
        session_id = cur.fetchone()[0]
        self.conn.commit()
        cur.close()
        return session_id
    
    def save_response(self, senatair_id, session_id, question_data, answer):
        """Save a Senatair's response to the database"""
        cur = self.conn.cursor()
        
        try:
            cur.execute("""
                INSERT INTO senatair_responses 
                (senatair_id, session_id, question_text, answer_text, bill_number, question_type, matched_keywords)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                senatair_id,
                session_id,
                question_data.get('text', ''),
                answer,
                question_data.get('bill', ''),
                question_data.get('type', ''),
                ', '.join(question_data.get('matched_keywords', []))
            ))
            
            # Update daily answer count and policaps
            cur.execute("""
                UPDATE senatairs 
                SET daily_answer_count = daily_answer_count + 1,
                    policaps = policaps + 1,
                    last_active = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (senatair_id,))
            
            # Update session stats
            cur.execute("""
                UPDATE senatair_sessions 
                SET questions_answered = questions_answered + 1,
                    policaps_earned = policaps_earned + 1
                WHERE id = %s
            """, (session_id,))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ Error saving response: {e}")
            self.conn.rollback()
            return False
        finally:
            cur.close()
    
    def end_session(self, session_id):
        """End a Senatair session"""
        cur = self.conn.cursor()
        cur.execute("UPDATE senatair_sessions SET session_end = CURRENT_TIMESTAMP WHERE id = %s", (session_id,))
        self.conn.commit()
        cur.close()
    
    def get_senatair_stats(self, senatair_id):
        """Get comprehensive stats for a Senatair"""
        cur = self.conn.cursor()
        
        cur.execute("SELECT username, policaps, daily_answer_count FROM senatairs WHERE id = %s", (senatair_id,))
        user_data = cur.fetchone()
        
        cur.execute("SELECT COUNT(*) FROM senatair_responses WHERE senatair_id = %s", (senatair_id,))
        total_responses = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(DISTINCT bill_number) FROM senatair_responses WHERE senatair_id = %s", (senatair_id,))
        bills_engaged = cur.fetchone()[0]
        
        cur.close()
        
        return {
            'username': user_data[0],
            'policaps': float(user_data[1]),
            'daily_answers': user_data[2],
            'total_responses': total_responses,
            'bills_engaged': bills_engaged
        }
    
    def close(self):
        self.conn.close()

# Test the authentication system
def test_auth_system():
    auth = SenatairAuth()
    
    # Test creating a user
    user_id = auth.create_senatair("test_senatair", "test@senatai.ca")
    if user_id:
        print(f"✅ User created with ID: {user_id}")
        
        # Test session management
        session_id = auth.start_session(user_id)
        print(f"✅ Session started: {session_id}")
        
        # Test saving a response
        question_data = {
            'text': "How concerned are you about climate change?",
            'bill': 'C-12',
            'type': 'emotional',
            'matched_keywords': ['climate', 'change']
        }
        success = auth.save_response(user_id, session_id, question_data, "Very concerned")
        print(f"✅ Response saved: {success}")
        
        # Test getting stats
        stats = auth.get_senatair_stats(user_id)
        print(f"📊 User stats: {stats}")
        
        # End session
        auth.end_session(session_id)
        print("✅ Session ended")
    
    auth.close()

if __name__ == "__main__":
    test_auth_system()
