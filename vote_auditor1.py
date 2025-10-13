#!/usr/bin/env python3
import sqlite3
from datetime import datetime

class VoteAuditor:
    def __init__(self, db_name="survey_data.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
    
    def audit_predictions(self, Senatair_id=None, bill_text=None):
        """Audit predictions with filtering options"""
        query = "SELECT * FROM predicted_votes WHERE 1=1"
        params = []
        
        if Senatair_id:
            query += " AND Senatair_id = ?"
            params.append(Senatair_id)
        if bill_text:
            query += " AND bill_text LIKE ?"
            params.append(f"%{bill_text}%")
            
        self.cursor.execute(query, params)
        columns = [desc[0] for desc in self.cursor.description]
        results = self.cursor.fetchall()
        
        if not results:
            print("No matching predictions found")
            return []
            
        # Calculate accuracy for found predictions
        audits = []
        for row in results:
            row_dict = dict(zip(columns, row))
            accuracy = self._calculate_accuracy(row_dict)
            audits.append({**row_dict, 'accuracy': accuracy})
            
        return audits
    
    def _calculate_accuracy(self, prediction):
        """Compare prediction with actual Senatair votes"""
        # Get Senatair's actual vote on similar questions
        self.cursor.execute("""
            SELECT a.answer, a.score 
            FROM answers a
            JOIN questions q ON a.question_id = q.id
            WHERE a.Senatair_id = ? 
            AND q.question_text LIKE ?
        """, (prediction['Senatair_id'], f"%{prediction['bill_text']}%"))
        
        answers = self.cursor.fetchall()
        if not answers:
            return None  # No actual votes to compare with
            
        # Simple accuracy calculation
        predicted = prediction['predicted_vote'].lower()
        actual_positives = sum(1 for a in answers if (
            (a[0] == 'yes') or (a[1] and a[1] > 3)
        ))
        actual_negatives = sum(1 for a in answers if (
            (a[0] == 'no') or (a[1] and a[1] < 3)
        ))
        
        if predicted == 'yes':
            return actual_positives / (actual_positives + actual_negatives) if (actual_positives + actual_negatives) > 0 else None
        else:
            return actual_negatives / (actual_positives + actual_negatives) if (actual_positives + actual_negatives) > 0 else None
    
    def print_audit_report(self, audits):
        """Display audit results"""
        print("\nVOTE PREDICTION AUDIT REPORT")
        print("="*50)
        for audit in audits:
            print(f"\nBill: {audit['bill_text']}")
            print(f"User: {audit['Senatair_id']}")
            print(f"Model: {audit['predictor_model']}")
            print(f"Predicted: {audit['predicted_vote']}")
            if 'confidence' in audit:
                print(f"Confidence: {audit['confidence']:.0%}")
            if 'accuracy' in audit and audit['accuracy'] is not None:
                print(f"Actual Accuracy: {audit['accuracy']:.0%}")
            else:
                print("Actual Accuracy: No comparable votes found")
            print(f"Explanation: {audit['explanation']}")
            print(f"Timestamp: {audit['timestamp']}")
        print("\n" + "="*50)
    
    def close(self):
        self.conn.close()

if __name__ == "__main__":
    auditor = VoteAuditor()
    
    print("1. Audit all predictions")
    print("2. Audit by Senatair")
    print("3. Audit by bill text")
    choice = input("Select audit type (1-3): ")
    
    if choice == "1":
        audits = auditor.audit_predictions()
    elif choice == "2":
        Senatair = input("Enter Senatair ID: ")
        audits = auditor.audit_predictions(Senatair_id=Senatair)
    elif choice == "3":
        bill = input("Enter bill text to search: ")
        audits = auditor.audit_predictions(bill_text=bill)
    else:
        print("Invalid choice")
        audits = []
    
    auditor.print_audit_report(audits)
    auditor.close()
