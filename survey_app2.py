#!/usr/bin/env python3
from survey_database import init_db
from question_maker10 import generate_question  # Import your question generator
import sqlite3
from datetime import datetime
import random

class SurveySystem:
    def __init__(self):
        init_db()
        self.current_user = None
    
    def login(self, user_id):
        self.current_user = user_id
        print(f"Logged in as {user_id}")
    
    def generate_and_store_question(self):
        """Generate and store a new question using question_maker10"""
        question_text = generate_question()  # Use your question generator
        question_type = self.classify_question(question_text)
        theme = self.detect_theme(question_text)
        
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
    
    def classify_question(self, question_text):
        """Determine question type based on content"""
        if "rate" in question_text.lower() or "scale" in question_text.lower():
            return "scaled"
        elif " or " in question_text.lower() or " vs " in question_text.lower():
            return "comparison"
        return "opinion"
    
    def detect_theme(self, question_text):
        """Detect the theme from question text"""
        for theme, keywords in THEMES.items():
            if any(keyword in question_text.lower() for keyword in keywords):
                return theme
        return "general"
    
    # ... [keep all other existing methods from survey_app.py] ...

if __name__ == "__main__":
    system = SurveySystem()
    system.login("user123")
    
    # Generate and store 5 new questions
    for _ in range(5):
        system.generate_and_store_question()
    
    # Now get a random question to answer
    question = system.get_random_question()
    if question:
        qid, qtext = question
        print(f"\nQuestion: {qtext}")
        answer = input("Your answer: ")
        system.answer_question(qid, answer)
        print(f"Total tokens: {system.get_user_tokens()}")
    else:
        print("No questions available!")
