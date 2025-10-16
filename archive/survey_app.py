#!/usr/bin/env python3
from survey_database import init_db
import sqlite3
from datetime import datetime

class SurveySystem:
    def __init__(self):
        init_db()  # Ensure database exists
    
    def ask_question(self, question_text, question_type, theme=None):
        """Store a new question in the database"""
        conn = sqlite3.connect('survey_data.db')
        c = conn.cursor()
        c.execute('''INSERT INTO questions 
                    (question_text, question_type, theme, timestamp)
                    VALUES (?, ?, ?, ?)''',
                    (question_text, question_type, theme, datetime.now()))
        question_id = c.lastrowid
        conn.commit()
        conn.close()
        return question_id
    
    def answer_question(self, question_id, answer, Senatair_id=None, score=None):
        """Record an answer and reward tokens"""
        conn = sqlite3.connect('survey_data.db')
        c = conn.cursor()
        
        # Record answer
        c.execute('''INSERT INTO answers 
                    (question_id, answer, score, Senatair_id, timestamp)
                    VALUES (?, ?, ?, ?, ?)''',
                    (question_id, answer, score, Senatair_id, datetime.now()))
        
        # Update Senatair tokens if logged in
        if Senatair_id:
            c.execute('''UPDATE Senatairs 
                        SET tokens = tokens + 1,
                            last_active = ?
                        WHERE id = ?''',
                        (datetime.now(), Senatair_id))
            if c.rowcount == 0:  # New Senatair
                c.execute('''INSERT INTO Senatairs 
                            (id, tokens, last_active)
                            VALUES (?, 1, ?)''',
                            (Senatair_id, datetime.now()))
        
        conn.commit()
        conn.close()

if __name__ == "__main__":
    system = SurveySystem()
    
    # Example usage:
    qid = system.ask_question(
        "How important is climate change policy?",
        "scale_1_to_5",
        "environment"
    )
    
    system.answer_question(qid, "4", "user123")
    print("Question asked and answer recorded!")
