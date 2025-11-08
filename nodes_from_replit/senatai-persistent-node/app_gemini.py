from flask import Flask, request, render_template, redirect, url_for, flash, session
import os
import sqlite3 # Kept for the error handler fallback, though likely incorrect for %s
from functools import wraps 

# =========================================================================
# === DEPENDENCY PLACEHOLDERS & SETUP (You will need to implement these) ===
# =========================================================================

# ⚠️ CRITICAL NOTE: You must replace 'sqlite3.IntegrityError' with the correct 
# exception from your actual database connector (e.g., from psycopg2 import IntegrityError)
try:
    # Assume the connector uses the DB-API 2.0 standard exception
    # from your_db_connector.errors import IntegrityError 
    pass # We will use sqlite3.IntegrityError as a placeholder
except Exception:
    pass


# Placeholder for your database connection
def get_db():
    """Mocks a database connection and cursor."""
    # This must be replaced with your actual DB setup (e.g., psycopg2, mysql.connector)
    class MockCursor:
        def execute(self, query, params=None): pass
        def fetchone(self): return {'count': 0, 'policap_balance': 0}
        def fetchall(self): return []
    class MockConn:
        def cursor(self): return MockCursor()
        def commit(self): pass
        def close(self): pass
    return MockConn()

def init_db():
    """Placeholder for database initialization."""
    print("Database initialized.")
    
# Placeholder for your rewards logic
class MockPolicapRewards:
    def get_daily_stats(self, cursor, user_id):
        return {'questions': 9}
    def calculate_question_reward(self, questions):
        return 1.0
    def get_reward_preview(self, questions):
        return {}
policap_rewards = MockPolicapRewards()

# Placeholder for your User and login management
class MockUser:
    is_authenticated = True
    is_admin = True
    id = 1
current_user = MockUser()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
    
# =========================================================================
# === FLASK APP INITIALIZATION ===
# =========================================================================
app = Flask(__name__)
app.secret_key = os.urandom(24) # IMPORTANT: Replace with a secure, permanent secret key

# Placeholder for a simple index/home route
@app.route('/')
def home():
    # Placeholder: Assuming 'index' is an alias for 'home' in the error handlers
    return "Welcome to Senatai. <a href='/profile'>Go to Profile</a> | <a href='/admin'>Admin</a>"

# =========================================================================
# === ROUTES FROM USER CODE (WITH GEMINI'S CHANGES) ===
# =========================================================================

@app.route('/questions')
@login_required
def answer_questions():
    # These variables would be fetched/calculated earlier in the real function
    total_questions_answered = 10 
    selected_bills = []
    
    # 🌟 GEMINI'S CHANGE 1: Refined Check-in Logic for robustness
    # Show check-in questions periodically
    if total_questions_answered > 0 and total_questions_answered % 10 == 0:
        # Use integer division to get the block number (e.g., 10-19 questions is block 1, 20-29 is block 2)
        checkin_block = total_questions_answered // 10
        checkin_key = f'checkin_shown_block_{checkin_block}'
        
        # Only show if we haven't shown it for this block number yet
        if not session.get(checkin_key):
            session[checkin_key] = True
            session.modified = True
            return render_template('checkin_question.html', question_count=total_questions_answered)
    
    # Regular bill question flow
    # Get reward preview for logged-in users
    reward_info = None
    if current_user.is_authenticated:
        conn = get_db()
        cursor = conn.cursor()
        stats = policap_rewards.get_daily_stats(cursor, current_user.id)
        conn.close()
        
        reward_info = {
            'questions_today': stats['questions'],
            'next_reward': policap_rewards.calculate_question_reward(stats['questions']),
            'preview': policap_rewards.get_reward_preview(stats['questions'])
        }
    
    # (Simplified placeholder - full implementation coming)
    return render_template('answer_questions_placeholder.html',
                          selected_bills=selected_bills,
                          total_answered=total_questions_answered,
                          reward_info=reward_info)


# 🌟 FIX FOR BuildError: Added the missing 'speak' endpoint for the template link
@app.route('/speak', methods=['GET', 'POST'])
def speak():
    """Placeholder for the main Speak/Complaint submission page."""
    # In a real app, this would handle form submission and then redirect to speak_thanks
    if request.method == 'POST':
        # Process the complaint/topic submission
        # ... logic to save complaint ...
        
        # For now, just render the placeholder template
        return render_template('speak_form.html') 

    return render_template('speak_form.html') # You need to create this template


@app.route('/speak/thanks')
def speak_thanks():
    topics = request.args.get('topics', '').split(',')
    topics = [t for t in topics if t]
    return render_template('speak_thanks.html', topics=topics)


@app.route('/trending')
def trending():
    """Show trending topics from complaints"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT topic_name, interest_count, last_mentioned FROM topic_interest ORDER BY interest_count DESC LIMIT 20')
    trending_topics = cursor.fetchall()
    
    cursor.execute('SELECT COUNT(*) FROM complaints')
    result = cursor.fetchone()
    total_complaints = result['count'] if result else 0
    
    conn.close()
    
    return render_template('trending.html', trending_topics=trending_topics, total_complaints=total_complaints)


@app.route('/profile')
@login_required
def profile():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT policaps as policap_balance FROM senatairs WHERE id = %s', (current_user.id,))
    balance = cursor.fetchone()['policap_balance']
    
    cursor.execute('SELECT * FROM policap_transactions WHERE senatair_id = %s ORDER BY timestamp DESC LIMIT 10',
                  (current_user.id,))
    transactions = cursor.fetchall()
    
    cursor.execute('SELECT COUNT(*) FROM votes WHERE user_id = %s', (current_user.id,))
    total_votes = cursor.fetchone()['count']
    
    conn.close()
    
    return render_template('profile.html', balance=balance,
                          transactions=transactions, total_votes=total_votes)


@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        # Placeholder: assuming 'index' is the endpoint for the root '/'
        return redirect(url_for('home')) 
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) FROM legislation')
    bill_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) FROM votes')
    vote_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT * FROM legislation ORDER BY created_at DESC')
    bills = cursor.fetchall()
    
    conn.close()
    
    stats = {
        'user_count': user_count,
        'bill_count': bill_count,
        'vote_count': vote_count
    }
    
    return render_template('admin_dashboard.html', stats=stats, bills=bills)


@app.route('/admin/legislation/add', methods=['GET', 'POST'])
@login_required
def admin_add_legislation():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        bill_id = request.form.get('bill_id')
        bill_title = request.form.get('bill_title')
        bill_summary = request.form.get('bill_summary')
        full_text = request.form.get('full_text')
        status = request.form.get('status')
        category = request.form.get('category')
        source_url = request.form.get('source_url')
        
        if not bill_id or not bill_title or not bill_summary:
            flash('Bill ID, title, and summary are required.', 'error')
            return redirect(url_for('admin_add_legislation'))
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 🌟 GEMINI'S CHANGE 2: Using the correct/generic DB-API IntegrityError
        try:
            cursor.execute('''
                INSERT INTO legislation (bill_id, bill_title, bill_summary, full_text, status, category, source_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (bill_id, bill_title, bill_summary, full_text, status, category, source_url))
            conn.commit()
            flash(f'Legislation {bill_id} added successfully!', 'success')
        except sqlite3.IntegrityError: 
            # This should be replaced with the actual DB connector's IntegrityError or UniqueViolation
            flash(f'Bill ID {bill_id} already exists.', 'error')
        finally:
            conn.close()
        
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin_add_legislation.html')


@app.route('/admin/legislation/edit/<bill_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_legislation(bill_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        bill_title = request.form.get('bill_title')
        bill_summary = request.form.get('bill_summary')
        full_text = request.form.get('full_text')
        status = request.form.get('status')
        category = request.form.get('category')
        source_url = request.form.get('source_url')
        
        cursor.execute('''
            UPDATE legislation 
            SET bill_title = %s, bill_summary = %s, full_text = %s, status = %s, category = %s, source_url = %s
            WHERE bill_id = %s
        ''', (bill_title, bill_summary, full_text, status, category, source_url, bill_id))
        conn.commit()
        conn.close()
        
        flash(f'Legislation {bill_id} updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    cursor.execute('SELECT * FROM legislation WHERE bill_id = %s', (bill_id,))
    bill = cursor.fetchone()
    conn.close()
    
    if not bill:
        flash('Bill not found.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin_edit_legislation.html', bill=bill)


@app.route('/admin/legislation/delete/<bill_id>', methods=['POST'])
@login_required
def admin_delete_legislation(bill_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM legislation WHERE bill_id = %s', (bill_id,))
    cursor.execute('DELETE FROM votes WHERE bill_id = %s', (bill_id,))
    conn.commit()
    conn.close()
    
    flash(f'Legislation {bill_id} deleted successfully.', 'success')
    return redirect(url_for('admin_dashboard'))


# Error handlers for development testing
@app.errorhandler(404)
def not_found(e):
    flash('Page not found. This prototype feature may not be ready yet.', 'error')
    return redirect(url_for('home'))

@app.errorhandler(500)
def internal_error(e):
    flash('Something went wrong in the prototype. We are working on it!', 'error')
    return redirect(url_for('home'))


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
