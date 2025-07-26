from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    policaps = db.Column(db.Float, default=0.0)
    last_active = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    category = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    summary = db.Column(db.Text)
    full_text = db.Column(db.Text)
    predicted_yes = db.Column(db.Float)  # Percentage prediction
    predicted_no = db.Column(db.Float)
    actual_yes = db.Column(db.Float)     # After overrides
    actual_no = db.Column(db.Float)
    audit_rate = db.Column(db.Float)     # Percentage of votes audited
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    voting_deadline = db.Column(db.DateTime)

class UserVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'))
    predicted_vote = db.Column(db.String(16))  # 'yes' or 'no'
    final_vote = db.Column(db.String(16))     # After override
    policaps_spent = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
