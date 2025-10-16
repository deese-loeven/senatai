import sqlite3
from collections import Counter
import re

class VotePredictor:
    def __init__(self, db_path='senatai.db', threshold=0.2):
        self.db_path = db_path
        self.threshold = threshold
        self.positive_kws = ['clean', 'climate', 'child', 'support', 'protect', 'reduction', 'amend', 'establish', 'promote']
        self.negative_kws = ['pollution', 'criminal', 'oppose', 'deny', 'harm', 'resume']  # Tune per domain

    def normalize_response(self, score, q_type):
        """Map 1-4 to -1..1; reverse for 'positive' Qs (low #=high support), flip for 'concern'."""
        base = (score - 2.5) / 1.5  # 1=-1, 4=1
        if q_type in ['optimism', 'significance', 'supportive', 'prioritize_positive']:  # Low # = high support
            return -base  # Flip: 1=1, 4=-1
        elif q_type in ['concern', 'frustrated', 'worried', 'prioritize_negative']:  # Low # = low support
            return base
        return base  # Neutral/default

    def get_bill_sentiment(self, bill_summary):
        """Simple keyword count for bill lean."""
        words = re.findall(r'\b\w+\b', bill_summary.lower())
        pos = sum(1 for w in words if any(kw in w for kw in self.positive_kws))
        neg = sum(1 for w in words if any(kw in w for kw in self.negative_kws))
        return (pos - neg) / len(words) if words else 0

    def predict_from_responses(self, responses, bill_summary, question_types=None):
        """Core: responses=[scores], types=['optimism',...]; return 'Yes'/'No'/'Unsure'."""
        if not responses:
            return 'Unsure'

        n_types = question_types or ['neutral'] * len(responses)
        user_scores = [self.normalize_response(score, q_type) for score, q_type in zip(responses, n_types)]
        avg_user = sum(user_scores) / len(user_scores)

        bill_sent = self.get_bill_sentiment(bill_summary)
        pred_score = 0.8 * avg_user + 0.2 * bill_sent  # User-heavy

        if pred_score > self.threshold:
            return 'Yes'
        elif pred_score < -self.threshold:
            return 'No'
        return 'Unsure'

    def predict_for_user(self, user_id, bill_id):
        """DB-integrated: Pull responses for user+bill, get summary, predict."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Fetch responses (assume table: responses(user_id, bill_id, question_type, choice 1-4))
        cur.execute("SELECT question_type, choice FROM responses WHERE user_id=? AND bill_id=?", (user_id, bill_id))
        resp_data = cur.fetchall()  # [('optimism', 2), ('significance', 2), ...]
        responses = [choice for _, choice in resp_data]
        q_types = [q_type for q_type, _ in resp_data]

        # Fetch bill summary (assume bills table: bill_id, summary)
        cur.execute("SELECT summary FROM bills WHERE bill_id=?", (bill_id,))
        bill_row = cur.fetchone()
        bill_summary = bill_row[0] if bill_row else "No summary available"

        conn.close()
        return self.predict_from_responses(responses, bill_summary, q_types)

# Example usage / test
if __name__ == "__main__":
    predictor = VotePredictor()

    # Dan's C-468: [2 (somewhat optimistic), 2 (somewhat significant)]
    dan_pred = predictor.predict_from_responses([2, 2], "Part 1 of this enactment amends the Canadian Environmental Protection Act, 1999 to promote the reduction of air pollution and the quality of outdoor air.", ['optimism', 'significance'])
    print(f"Dan on C-468: {dan_pred}")

    # Chantelle's C-701: [4 (not worried=high support), 2 (no, prioritize child=positive lean), 1 (very significant=high)]
    chantelle_pred = predictor.predict_from_responses([4, 2, 1], "This enactment provides for the establishment of the Office of the Commissioner for Children and Young Persons in Canada.", ['concern', 'prioritize_child', 'significance'])
    print(f"Chantelle on C-701: {chantelle_pred}")
