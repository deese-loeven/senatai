import sqlite3
from datetime import datetime, date
import tkinter as tk
from tkinter import ttk, messagebox
from question_maker10 import generate_question

class SurveyWindow:
    def __init__(self, master, db_name="survey_data.db", user_id=""):
        self.master = master
        self.user_id = user_id
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        
        # Window setup
        master.title(f"Survey Session - {user_id}")
        master.geometry("600x400")
        
        # Question display
        self.question_frame = ttk.Frame(master, padding="20")
        self.question_frame.pack(fill=tk.BOTH, expand=True)
        
        self.question_label = ttk.Label(
            self.question_frame, 
            text="", 
            wraplength=500,
            font=('Helvetica', 12)
        )
        self.question_label.pack(pady=20)
        
        # Answer interface
        self.answer_frame = ttk.Frame(self.question_frame)
        self.answer_frame.pack(pady=20)
        
        self.scale_buttons = []
        self.yn_buttons = []
        
        # Stats display
        self.stats_label = ttk.Label(
            self.question_frame,
            text="",
            font=('Helvetica', 10)
        )
        self.stats_label.pack(pady=10)
        
        # Navigation
        self.nav_frame = ttk.Frame(master)
        self.nav_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            self.nav_frame, 
            text="Exit", 
            command=self.on_close
        ).pack(side=tk.RIGHT)
        
        # Initialize
        self.questions_answered = 0
        self.current_question = None
        self.setup_question_types()
        self.load_next_question()
        self.update_stats()
        
        # Handle window close
        master.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def setup_question_types(self):
        # Scale question interface
        scale_frame = ttk.Frame(self.answer_frame)
        self.scale_frame = scale_frame
        
        ttk.Label(scale_frame, text="1 = Strongly disagree").grid(row=0, column=0)
        ttk.Label(scale_frame, text="5 = Strongly agree").grid(row=0, column=4)
        
        for i in range(1, 6):
            btn = ttk.Button(
                scale_frame, 
                text=str(i), 
                width=3,
                command=lambda x=i: self.record_answer(str(x), x)
            )
            btn.grid(row=1, column=i-1, padx=5)
            self.scale_buttons.append(btn)
        
        # Yes/No question interface
        yn_frame = ttk.Frame(self.answer_frame)
        self.yn_frame = yn_frame
        
        ttk.Button(
            yn_frame, 
            text="Yes", 
            width=8,
            command=lambda: self.record_answer("yes", 1)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            yn_frame, 
            text="No", 
            width=8,
            command=lambda: self.record_answer("no", 0)
        ).pack(side=tk.LEFT, padx=5)
    
    def load_next_question(self):
        """Get a new question the user hasn't answered"""
        self.cursor.execute("""
            SELECT q.id, q.question_text, q.question_type 
            FROM questions q
            WHERE q.id NOT IN (
                SELECT a.question_id 
                FROM answers a 
                WHERE a.user_id = ?
            )
            ORDER BY RANDOM() 
            LIMIT 1
        """, (self.user_id,))
        
        question = self.cursor.fetchone()
        
        if not question:
            messagebox.showinfo(
                "Complete", 
                "You've answered all available questions!"
            )
            self.master.destroy()
            return
        
        self.current_question = {
            'id': question[0],
            'text': question[1],
            'type': question[2]
        }
        
        self.question_label.config(text=self.current_question['text'])
        
        # Show appropriate answer interface
        if self.current_question['type'] == "scale_1_to_5":
            self.yn_frame.pack_forget()
            self.scale_frame.pack()
        else:
            self.scale_frame.pack_forget()
            self.yn_frame.pack()
    
    def record_answer(self, answer_text, score):
        """Save answer and load next question"""
        if not self.current_question:
            return
            
        try:
            # Record answer
            self.cursor.execute("""
                INSERT INTO answers 
                (question_id, answer, score, user_id) 
                VALUES (?, ?, ?, ?)
            """, (
                self.current_question['id'],
                answer_text,
                score,
                self.user_id
            ))
            
            # Update user stats
            self.cursor.execute("""
                UPDATE users 
                SET policap = policap + ?,
                    daily_answer_count = daily_answer_count + 1,
                    last_active = ?
                WHERE id = ?
            """, (
                self.calculate_policap(),
                datetime.now(),
                self.user_id
            ))
            
            self.conn.commit()
            self.questions_answered += 1
            self.update_stats()
            self.load_next_question()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to record answer: {str(e)}")
    
    def calculate_policap(self):
        """Calculate policap based on answer count"""
        self.cursor.execute(
            "SELECT COUNT(*) FROM answers WHERE user_id = ?",
            (self.user_id,)
        )
        answer_count = self.cursor.fetchone()[0]
        
        if answer_count < 10:
            return 1.0
        elif answer_count < 100:
            return round(1.0 - (answer_count - 10) * (1.0 - 0.01) / 90, 3)
        elif answer_count < 200:
            return 0.01
        else:
            return 0.001
    
    def update_stats(self):
        """Update the stats display"""
        self.cursor.execute("""
            SELECT policap, daily_answer_count 
            FROM users 
            WHERE id = ?
        """, (self.user_id,))
        
        policap, daily_count = self.cursor.fetchone()
        self.stats_label.config(
            text=f"Session: {self.questions_answered} answered | Today: {daily_count} | Total policap: {policap:.3f}"
        )
    
    def on_close(self):
        """Handle window close"""
        self.conn.close()
        self.master.destroy()

def launch_survey_window(user_id):
    root = tk.Tk()
    SurveyWindow(root, user_id=user_id)
    root.mainloop()

# Example usage:
# launch_survey_window("test_user123")
