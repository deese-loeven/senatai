# authentication_template.py
# SENATAI Authentication Template
# Copy this and customize for your deployment

import psycopg2
import hashlib
import secrets
from datetime import datetime, date

class AuthTemplate:
    def __init__(self, db_config):
        self.db_config = db_config
        
    def get_connection(self):
        return psycopg2.connect(**self.db_config)
    
    def hash_password(self, password):
        """Basic password hashing - enhance for production"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, email, password):
        """Create a new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            hashed_pw = self.hash_password(password)
            cursor.execute("""
                INSERT INTO senatairs (username, email, policaps) 
                VALUES (%s, %s, 25.0)
                RETURNING id
            """, (username, email))
            
            user_id = cursor.fetchone()[0]
            conn.commit()
            return user_id
            
        except psycopg2.IntegrityError:
            conn.rollback()
            raise ValueError("Username already exists")
        finally:
            cursor.close()
            conn.close()
    
    def authenticate_user(self, username, password):
        """Authenticate a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # In production, you'd verify hashed passwords
        # For template, we'll use simple username match
        cursor.execute("""
            SELECT id, username, policaps FROM senatairs 
            WHERE username = %s
        """, (username,))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'policaps': user[2]
            }
        return None
    
    def update_user_activity(self, user_id):
        """Update user's last active timestamp"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE senatairs 
            SET last_active = %s 
            WHERE id = %s
        """, (datetime.now(), user_id))
        
        conn.commit()
        cursor.close()
        conn.close()
    
    def award_policaps(self, user_id, amount):
        """Award policaps to user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE senatairs 
            SET policaps = policaps + %s,
                daily_answer_count = daily_answer_count + 1,
                last_active = %s
            WHERE id = %s
        """, (amount, datetime.now(), user_id))
        
        conn.commit()
        cursor.close()
        conn.close()

# Example configuration
SAMPLE_DB_CONFIG = {
    'dbname': 'your_database_name',
    'user': 'your_username',
    'password': 'your_password',
    'host': 'localhost'
}

# Usage example:
if __name__ == "__main__":
    auth = AuthTemplate(SAMPLE_DB_CONFIG)
    
    # Create a test user
    try:
        user_id = auth.create_user("test_user", "test@example.com", "password123")
        print(f"Created user with ID: {user_id}")
    except ValueError as e:
        print(f"Error: {e}")
    
    # Authenticate user
    user = auth.authenticate_user("test_user", "password123")
    if user:
        print(f"Authenticated: {user['username']} with {user['policaps']} policaps")
