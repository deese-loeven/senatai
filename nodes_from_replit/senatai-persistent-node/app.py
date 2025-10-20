"""
Senatai Persistent Node
========================
Multi-user web server version designed for persistent online deployment.
Uses PostgreSQL for scalable, network-accessible data storage.
Serves as P2P hub for mobile apps and Sovereign Nodes.
"""
import os
from decimal import Decimal
import psycopg2
import psycopg2.extras
import random
import uuid
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import question_generator
import topic_matcher
import icebreakers
import demographics
import policap_rewards
import badges
# Environment-based configuration only



app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'CHANGE-THIS-IN-PRODUCTION')
app.config['ADMIN_USERNAME'] = os.environ.get('ADMIN_USERNAME', 'admin')
app.config['ADMIN_PASSWORD_HASH'] = generate_password_hash(os.environ.get('ADMIN_PASSWORD', 'changetheadminpassword'))

# PostgreSQL connection from environment
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable not set. "
        "Set it to: postgresql://user:password@host:port/database"
    )

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, id, username, policap_balance, is_admin=False):
        self.id = id
        self.username = username
        self.policap_balance = policap_balance
        self.is_admin = is_admin


@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, policaps as policap_balance, CAST(is_admin AS INTEGER) as is_admin FROM senatairs WHERE id = %s', (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        return User(user_data['id'], user_data['username'], user_data['policap_balance'], user_data['is_admin'])
    return None


def get_db():
    """Get PostgreSQL database connection from environment variable"""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    return conn


def init_db():
    """Initialize PostgreSQL database schema"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            policap_balance DECIMAL(10,2) DEFAULT 0.00,
            lifetime_policap_earned DECIMAL(10,2) DEFAULT 0.00,
            total_audits_made INTEGER DEFAULT 0,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            accepted_terms BOOLEAN DEFAULT FALSE,
            accepted_coop_agreement BOOLEAN DEFAULT FALSE
        )
    """)
    
    # Legislation table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS legislation (
            id SERIAL PRIMARY KEY,
            bill_id VARCHAR(50) UNIQUE NOT NULL,
            bill_title TEXT NOT NULL,
            bill_summary TEXT NOT NULL,
            full_text TEXT,
            status VARCHAR(50) NOT NULL,
            category VARCHAR(100),
            source_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Votes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            bill_id VARCHAR(50) NOT NULL,
            vote VARCHAR(10) NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Policap transactions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS policap_transactions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            amount DECIMAL(10,2) NOT NULL,
            transaction_type VARCHAR(50) NOT NULL,
            description TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Daily question count
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_question_count (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            activity_date DATE NOT NULL,
            question_count INTEGER DEFAULT 0,
            vote_count INTEGER DEFAULT 0,
            UNIQUE(user_id, activity_date)
        )
    """)
    
    # Questions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id SERIAL PRIMARY KEY,
            bill_id VARCHAR(50) NOT NULL,
            question_text TEXT NOT NULL,
            question_type VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Question responses
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS question_responses (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            question_id INTEGER NOT NULL REFERENCES questions(id),
            bill_id VARCHAR(50) NOT NULL,
            response_text TEXT NOT NULL,
            session_id VARCHAR(100),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Complaints
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id SERIAL PRIMARY KEY,
            complaint_text TEXT NOT NULL,
            session_id VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Topic interest
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topic_interest (
            id SERIAL PRIMARY KEY,
            topic VARCHAR(200) NOT NULL,
            interest_count INTEGER DEFAULT 1,
            last_mentioned TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Demographic data
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS demographic_data (
            id SERIAL PRIMARY KEY,
            user_id INTEGER UNIQUE REFERENCES users(id),
            session_id VARCHAR(100) UNIQUE,
            age_range VARCHAR(50),
            gender VARCHAR(50),
            region VARCHAR(100),
            work_experience TEXT,
            expertise_areas TEXT,
            education_level VARCHAR(50),
            provided_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Vote predictions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vote_predictions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            bill_id VARCHAR(50) NOT NULL,
            predicted_vote VARCHAR(10) NOT NULL,
            confidence DECIMAL(5,2),
            module_name VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Policap spending
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS policap_spending (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            bill_id VARCHAR(50) NOT NULL,
            policap_spent DECIMAL(10,2) NOT NULL,
            spending_type VARCHAR(20) NOT NULL,
            position_change_reason TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Question modules
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS question_modules (
            id SERIAL PRIMARY KEY,
            module_name VARCHAR(100) UNIQUE NOT NULL,
            module_description TEXT,
            version VARCHAR(20),
            rating DECIMAL(3,1) DEFAULT 0.0,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Predictor modules
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictor_modules (
            id SERIAL PRIMARY KEY,
            module_name VARCHAR(100) UNIQUE NOT NULL,
            module_description TEXT,
            version VARCHAR(20),
            rating DECIMAL(3,1) DEFAULT 0.0,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    if current_user.is_authenticated:
        if not current_user.is_admin and (not hasattr(current_user, 'accepted_terms') or session.get('needs_agreements')):
            return redirect(url_for('agreements'))
        return redirect(url_for('home'))
    return redirect(url_for('home'))


@app.route('/favicon.ico')
def favicon():
    """Return empty favicon to prevent 404 errors"""
    return '', 204

@app.route('/home')
def home():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM legislation')
    bill_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) FROM complaints')
    total_complaints = cursor.fetchone()['count']
    
    balance = 0
    vote_count = 0
    total_votes = 0
    
    if current_user.is_authenticated:
        cursor.execute('SELECT policaps as policap_balance FROM senatairs WHERE id = %s', (current_user.id,))
        balance = cursor.fetchone()['policap_balance']
        
        cursor.execute('SELECT COUNT(*) as count FROM votes WHERE user_id = %s', (current_user.id,))
        vote_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) FROM votes')
        total_votes = cursor.fetchone()['count']
    
    conn.close()
    
    return render_template('home.html', 
                         bill_count=bill_count, 
                         total_complaints=total_complaints,
                         balance=balance,
                         vote_count=vote_count,
                         total_votes=total_votes)


@app.route('/answer_questions')
def answer_questions():
    """Main entry point for the Answer Questions flow - starts with Post and Ghost"""
    return redirect(url_for('speak'))


@app.route('/audit_predictions')
def audit_predictions():
    """Audit vote predictions - requires login"""
    if not current_user.is_authenticated:
        flash('Please create an account to audit predictions and earn Policap.', 'error')
        return redirect(url_for('signup'))
    
    return render_template('audit_predictions.html')


@app.route('/consensus_forums')
def consensus_forums():
    """View consensus data and forums for bills"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT bill_id, bill_title, bill_summary, category, status FROM legislation ORDER BY bill_id DESC LIMIT 50')
    bills = cursor.fetchall()
    
    conn.close()
    
    return render_template('consensus_forums.html', bills=bills)


@app.route('/settings')
def settings():
    """User settings and preferences"""
    return render_template('settings.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required.', 'error')
            return redirect(url_for('signup'))
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
        if cursor.fetchone():
            flash('Username already exists. Please choose another.', 'error')
            conn.close()
            return redirect(url_for('signup'))
        
        password_hash = generate_password_hash(password)
        cursor.execute('INSERT INTO senatairs (username, password_hash) VALUES (%s, %s)', (username, password_hash))
        conn.commit()
        conn.close()
        
        flash('Account created successfully! Please review and accept our agreements.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required.', 'error')
            return render_template('login.html')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, password_hash, policaps as policap_balance, is_admin, accepted_terms, accepted_coop_agreement FROM senatairs WHERE username = %s', (username,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(user_data['id'], user_data['username'], user_data['policap_balance'], user_data['is_admin'])
            login_user(user)
            
            if not user_data['accepted_terms'] or not user_data['accepted_coop_agreement']:
                session['needs_agreements'] = True
                return redirect(url_for('agreements'))
            
            return redirect(url_for('vote'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


@app.route('/agreements', methods=['GET', 'POST'])
@login_required
def agreements():
    if request.method == 'POST':
        accept_terms = request.form.get('accept_terms')
        accept_coop = request.form.get('accept_coop')
        
        if accept_terms and accept_coop:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('UPDATE senatairs SET accepted_terms = TRUE, accepted_coop_agreement = TRUE WHERE id = %s',
                          (current_user.id,))
            conn.commit()
            conn.close()
            
            session.pop('needs_agreements', None)
            flash('Welcome to Senatai! You\'re now part of the cooperative.', 'success')
            return redirect(url_for('vote'))
        else:
            flash('You must accept both agreements to continue.', 'error')
    
    return render_template('agreements.html')


@app.route('/vote', methods=['GET', 'POST'])
@login_required
def vote():
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        vote_count = 0
        question_responses = []
        
        for key, value in request.form.items():
            if key.startswith('vote_'):
                bill_id = key.replace('vote_', '')
                cursor.execute('INSERT INTO votes (user_id, bill_id, vote) VALUES (%s, %s, %s)',
                             (current_user.id, bill_id, value))
                vote_count += 1
            elif key.startswith('q_'):
                parts = key.split('_')
                if len(parts) >= 3:
                    question_id = parts[1]
                    bill_id = '_'.join(parts[2:])
                    question_responses.append({
                        'question_id': question_id,
                        'bill_id': bill_id,
                        'value': value
                    })
        
        if vote_count > 0:
            reward = calculate_policap_reward(current_user.id)
            
            cursor.execute('UPDATE senatairs SET policaps = policaps + %s WHERE id = %s',
                          (reward, current_user.id))
            cursor.execute('INSERT INTO policap_transactions (user_id, amount, transaction_type, description) VALUES (%s, %s, %s, %s)',
                          (current_user.id, reward, 'voting_reward', f'Reward for voting on {vote_count} bills'))
            conn.commit()
            
            current_user.policap_balance += reward
            
            if question_responses:
                save_question_responses(current_user.id, question_responses)
            
            flash(f'Your votes and responses have been recorded! You earned {reward:.2f} Policap.', 'success')
        
        conn.close()
        return redirect(url_for('profile'))
    
    cursor.execute('SELECT bill_id FROM votes WHERE user_id = %s', (current_user.id,))
    voted_bills = [row['bill_id'] for row in cursor.fetchall()]
    
    if voted_bills:
        placeholders = ','.join(['%s' for _ in voted_bills])
        cursor.execute(f'SELECT bill_id, bill_title, bill_summary, status, category FROM legislation WHERE bill_id NOT IN ({placeholders})',
                      voted_bills)
    else:
        cursor.execute('SELECT bill_id, bill_title, bill_summary, status, category FROM legislation')
    
    all_available_bills = cursor.fetchall()
    conn.close()
    
    if len(all_available_bills) < 5:
        bills = all_available_bills
    else:
        bills = random.sample(all_available_bills, 5)
    
    bills_with_questions = []
    for bill in bills:
        bill_dict = {
            'bill_id': bill['bill_id'],
            'bill_title': bill['bill_title'],
            'bill_summary': bill['bill_summary'],
            'status': bill['status'],
            'category': bill.get('category', 'General')
        }
        
        questions = save_questions_for_bill(bill['bill_id'], bill['bill_title'], bill['bill_summary'], bill_dict['category'])
        bill_dict['questions'] = questions
        bills_with_questions.append(bill_dict)
    
    return render_template('vote.html', bills=bills_with_questions)


@app.route('/consensus/<bill_id>')
@login_required
def consensus(bill_id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT bill_id, bill_title, bill_summary, status FROM legislation WHERE bill_id = %s', (bill_id,))
    bill = cursor.fetchone()
    
    if not bill:
        flash('Bill not found.', 'error')
        conn.close()
        return redirect(url_for('vote'))
    
    cursor.execute('SELECT vote, COUNT(*) FROM votes WHERE bill_id = %s GROUP BY vote', (bill_id,))
    vote_counts = dict(cursor.fetchall())
    
    total_votes = sum(vote_counts.values())
    
    cursor.execute('''
        SELECT AVG(CASE WHEN spending_type = 'agree' THEN policap_spent ELSE 0 END) as avg_agree,
               AVG(CASE WHEN spending_type = 'disagree' THEN policap_spent ELSE 0 END) as avg_disagree
        FROM policap_spending WHERE bill_id = %s
    ''', (bill_id,))
    spending_data = cursor.fetchone()
    
    conn.close()
    
    consensus_data = {
        'bill': bill,
        'vote_counts': vote_counts,
        'total_votes': total_votes,
        'spending_data': spending_data
    }
    
    return render_template('consensus.html', data=consensus_data)


@app.route('/modules/questions')
@login_required
def question_modules():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM question_modules WHERE is_active = 1')
    modules = cursor.fetchall()
    conn.close()
    
    return render_template('question_modules.html', modules=modules)


@app.route('/modules/predictors')
@login_required
def predictor_modules():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM predictor_modules WHERE is_active = 1')
    modules = cursor.fetchall()
    conn.close()
    
    return render_template('predictor_modules.html', modules=modules)


@app.route('/find-rep')
@login_required
def find_rep():
    representatives = [
        {'riding': 'Toronto Centre', 'name': 'Hon. Chrystia Freeland', 'email': 'chrystia.freeland@parl.gc.ca'},
        {'riding': 'Vancouver Granville', 'name': 'Taleeb Noormohamed', 'email': 'taleeb.noormohamed@parl.gc.ca'},
        {'riding': 'Calgary Centre', 'name': 'Hon. Greg McLean', 'email': 'greg.mclean@parl.gc.ca'},
        {'riding': 'Montreal Ville-Marie', 'name': 'Rachel Bendayan', 'email': 'rachel.bendayan@parl.gc.ca'},
        {'riding': 'Ottawa Centre', 'name': 'Yasir Naqvi', 'email': 'yasir.naqvi@parl.gc.ca'},
        {'riding': 'Edmonton Centre', 'name': 'Randy Boissonnault', 'email': 'randy.boissonnault@parl.gc.ca'},
        {'riding': 'Winnipeg Centre', 'name': 'Leah Gazan', 'email': 'leah.gazan@parl.gc.ca'},
        {'riding': 'Halifax', 'name': 'Andy Fillmore', 'email': 'andy.fillmore@parl.gc.ca'},
        {'riding': 'Regina-Wascana', 'name': 'Michael Kram', 'email': 'michael.kram@parl.gc.ca'},
        {'riding': 'Victoria', 'name': 'Laurel Collins', 'email': 'laurel.collins@parl.gc.ca'}
    ]
    
    return render_template('find_rep.html', representatives=representatives)


@app.route('/speak', methods=['GET', 'POST'])
def speak():
    """Post and Ghost - Anonymous complaint submission"""
    if request.method == 'POST':
        complaint_text = request.form.get('complaint')
        
        # Allow "quit" to exit and go to homepage
        if complaint_text and complaint_text.strip().lower() == 'quit':
            return redirect(url_for('home'))
        
        if not complaint_text or len(complaint_text.strip()) < 5:
            flash('Please share at least a few words with us.', 'error')
            return redirect(url_for('speak'))
        
        # Get or create guest session ID
        if 'guest_id' not in session:
            session['guest_id'] = str(uuid.uuid4())
        
        guest_id = session['guest_id']
        
        # Extract topics
        topics = topic_matcher.extract_topics_from_text(complaint_text)
        
        # Get all bills for matching
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT bill_id, bill_title, bill_summary, status, category FROM legislation')
        all_bills = cursor.fetchall()
        
        # Match to bills
        matched_bill_ids = topic_matcher.match_bills_to_complaint(complaint_text, all_bills)
        
        # Save complaint
        cursor.execute('''
            INSERT INTO complaints (complaint_text, guest_session_id, detected_topics, matched_bills, matched_categories)
            VALUES (%s, %s, %s, %s, %s)
        ''', (complaint_text, guest_id, ','.join(topics), ','.join(matched_bill_ids), ','.join(topics)))
        
        # Update topic interest counts
        for topic in topics:
            cursor.execute('SELECT id, interest_count FROM topic_interest WHERE topic_name = %s', (topic,))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute('UPDATE topic_interest SET interest_count = interest_count + 1, last_mentioned = ? WHERE topic_name = %s',
                              (datetime.now(), topic))
            else:
                cursor.execute('INSERT INTO topic_interest (topic_name, category, interest_count) VALUES (%s, %s, %s)',
                              (topic, topic, 1))
        
        conn.commit()
        conn.close()
        
        # Store in session for bill selection
        session['complaint_text'] = complaint_text
        session['matched_bill_ids'] = matched_bill_ids
        session['detected_topics'] = topics
        
        # Redirect to bill selection instead of thanks page
        return redirect(url_for('select_bills'))
    
    # GET request - show form
    icebreaker = icebreakers.get_random_icebreaker()
    return render_template('speak.html', icebreaker=icebreaker)


@app.route('/select_bills', methods=['GET', 'POST'])
def select_bills():
    """Show 3-5 matched bills and let user select 1-2 to explore"""
    if 'matched_bill_ids' not in session:
        flash('Please start by sharing what\'s on your mind.', 'error')
        return redirect(url_for('speak'))
    
    if request.method == 'POST':
        selected_bills = request.form.getlist('selected_bills')
        
        if not selected_bills:
            flash('Please select at least one bill to explore, or type "quit" to exit.', 'error')
            return redirect(url_for('select_bills'))
        
        if len(selected_bills) > 2:
            flash('Please select maximum 2 bills to keep the session focused.', 'error')
            return redirect(url_for('select_bills'))
        
        # Store selected bills in session
        session['selected_bill_ids'] = selected_bills
        session['current_bill_index'] = 0
        session['questions_answered'] = 0
        
        # Start question sequence
        return redirect(url_for('answer_bill_questions'))
    
    # GET - show bill selection interface
    matched_ids = session.get('matched_bill_ids', [])
    complaint_text = session.get('complaint_text', '')
    
    if not matched_ids:
        # No matched bills - show a message and allow manual search or quit
        flash('We couldn\'t find specific legislation matching your concern. Try rephrasing or browse all bills.', 'info')
        return redirect(url_for('consensus_forums'))
    
    # Get bill details
    conn = get_db()
    cursor = conn.cursor()
    
    # Limit to 3-5 bills, prioritize most relevant
    display_ids = matched_ids[:5] if len(matched_ids) >= 5 else matched_ids[:3] if len(matched_ids) >= 3 else matched_ids
    
    placeholders = ','.join(['%s' for _ in display_ids])
    cursor.execute(f'SELECT bill_id, bill_title, bill_summary, status, category FROM legislation WHERE bill_id IN ({placeholders})', display_ids)
    matched_bills = cursor.fetchall()
    
    conn.close()
    
    # Mark most relevant (first 1-2 as green flagged)
    bills_with_relevance = []
    for i, bill in enumerate(matched_bills):
        bills_with_relevance.append({
            'bill_id': bill['bill_id'],
            'bill_title': bill['bill_title'],
            'bill_summary': bill['bill_summary'],
            'status': bill['status'],
            'category': bill.get('category', 'General'),
            'is_highly_relevant': i < 2  # Green flag first 2
        })
    
    return render_template('select_bills.html', bills=bills_with_relevance, complaint_text=complaint_text)


@app.route('/answer_bill_questions', methods=['GET', 'POST'])
def answer_bill_questions():
    """Answer questions about selected bills in sequence with demographics at Q15-20"""
    if 'selected_bill_ids' not in session:
        flash('Please select bills first.', 'error')
        return redirect(url_for('speak'))
    
    selected_bills = session.get('selected_bill_ids', [])
    total_questions_answered = session.get('total_questions_answered', 0)
    
    # Handle form submissions
    if request.method == 'POST':
        action = request.form.get('action')
        
        # Allow quit at any time
        if action == 'quit':
            return redirect(url_for('home'))
        
        # Handle demographic opt-in decision
        if action == 'demographic_decision':
            decision = request.form.get('decision')
            if decision == 'skip':
                session['skip_demographics'] = True
                return redirect(url_for('answer_bill_questions'))
            elif decision == 'learn_more':
                return render_template('demographic_explanation.html')
            else:  # answer
                session['providing_demographics'] = True
                return redirect(url_for('answer_bill_questions'))
        
        # Handle demographic question response
        if action == 'demographic_response':
            question_id = request.form.get('question_id')
            response = request.form.get('response')
            
            if 'demographic_responses' not in session:
                session['demographic_responses'] = []
            
            session['demographic_responses'].append({
                'question_id': question_id,
                'response': response
            })
            session['total_questions_answered'] = total_questions_answered + 1
            session.modified = True
            return redirect(url_for('answer_bill_questions'))
        
        # Handle regular question response
        if action == 'answer_question':
            # Award Policap for logged-in users
            if current_user.is_authenticated:
                conn = get_db()
                cursor = conn.cursor()
                reward = policap_rewards.award_question_policap(cursor, current_user.id, is_postgres=False)
                conn.commit()
                conn.close()
                
                # Flash reward notification
                if reward >= 1.0:
                    flash(f'🎉 Earned {reward} Policap!', 'success')
                elif reward >= 0.1:
                    flash(f'Earned {reward:.2f} Policap', 'info')
                else:
                    flash(f'Earned {reward:.3f} Policap (diminishing returns)', 'info')
            
            # Save the response (simplified for now)
            session['total_questions_answered'] = total_questions_answered + 1
            session.modified = True
            return redirect(url_for('answer_bill_questions'))
    
    # GET: Determine what to show next
    
    # Check if at demographic collection point (questions 15-20)
    if total_questions_answered >= 15 and total_questions_answered < 21:
        if not session.get('skip_demographics') and not session.get('demographics_offered'):
            # Show demographic intro/decision
            session['demographics_offered'] = True
            intro = demographics.get_demographic_intro_message()
            return render_template('demographic_intro.html', intro=intro)
        
        if session.get('providing_demographics'):
            # Show next demographic question
            responses_so_far = session.get('demographic_responses', [])
            next_q = demographics.get_next_demographic_question(responses_so_far)
            
            if next_q:
                return render_template('demographic_question.html', question=next_q, 
                                     progress=total_questions_answered)
            else:
                # Finished demographics, continue with bill questions
                session['providing_demographics'] = False
                session.modified = True
    
    # Show sign-up prompt after 4 questions
    if total_questions_answered == 4 and not session.get('signup_prompted'):
        session['signup_prompted'] = True
        session.modified = True
        return render_template('signup_prompt.html', is_guest=not current_user.is_authenticated)
    
    # Show check-in questions periodically
    if total_questions_answered > 0 and total_questions_answered % 10 == 0:
        if not session.get(f'checkin_shown_{total_questions_answered}'):
            session[f'checkin_shown_{total_questions_answered}'] = True
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
    total_complaints = cursor.fetchone()['topic_name']
    
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
        return redirect(url_for('index'))
    
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
        return redirect(url_for('index'))
    
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
        
        try:
            cursor.execute('''
                INSERT INTO legislation (bill_id, bill_title, bill_summary, full_text, status, category, source_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (bill_id, bill_title, bill_summary, full_text, status, category, source_url))
            conn.commit()
            flash(f'Legislation {bill_id} added successfully!', 'success')
        except sqlite3.IntegrityError:
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
        return redirect(url_for('index'))
    
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
            SET bill_title = ?, bill_summary = ?, full_text = ?, status = ?, category = ?, source_url = ?
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
        return redirect(url_for('index'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM legislation WHERE bill_id = %s', (bill_id,))
    cursor.execute('DELETE FROM votes WHERE bill_id = %s', (bill_id,))
    conn.commit()
    conn.close()
    
    flash(f'Legislation {bill_id} deleted successfully.', 'success')
    return redirect(url_for('admin_dashboard'))



if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
