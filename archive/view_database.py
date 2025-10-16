#!/usr/bin/env python3
import sqlite3
from tabulate import tabulate

def view_all_data():
    conn = sqlite3.connect('survey_data.db')
    c = conn.cursor()
    
    print("\n=== Questions Table ===")
    c.execute("SELECT * FROM questions")
    print(tabulate(c.fetchall(), headers=["ID", "Text", "Type", "Theme", "Timestamp"]))
    
    print("\n=== Answers Table ===")
    c.execute("SELECT * FROM answers")
    print(tabulate(c.fetchall(), headers=["ID", "QID", "Answer", "Score", "User", "Timestamp"]))
    
    print("\n=== Users Table ===")
    c.execute("SELECT * FROM users")
    print(tabulate(c.fetchall(), headers=["ID", "Tokens", "Last Active"]))
    
    conn.close()

if __name__ == "__main__":
    view_all_data()
