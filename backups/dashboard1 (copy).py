@app.route('/dashboard')
@login_required
def dashboard():
    # Update last active time
    current_user.last_active = datetime.utcnow()
    db.session.commit()
    
    return render_template('dashboard.html',
                         policaps=current_user.policaps)
@app.route('/answer-questions')
@login_required
def answer_questions():
    # Get unanswered questions
    answered_ids = [a.question_id for a in 
                   Answer.query.filter_by(user_id=current_user.id).all()]
    
    questions = Question.query.filter(
        Question.active == True,
        ~Question.id.in_(answered_ids)
    ).order_by(db.func.random()).limit(10).all()
    
    return render_template('answer_questions.html',
                         questions=questions,
                         policaps=current_user.policaps)
@app.route('/audit-predictions')
@login_required
def audit_predictions():
    # Get bills with predictions but no final vote from user
    voted_bills = [v.bill_id for v in 
                  UserVote.query.filter_by(user_id=current_user.id).all()]
    
    bills = Bill.query.filter(
        Bill.voting_deadline > datetime.utcnow(),
        ~Bill.id.in_(voted_bills)
    ).order_by(Bill.voting_deadline.asc()).all()
    
    # Add predictions for each bill
    for bill in bills:
        bill.user_prediction = predict_vote(current_user.id, bill)
    
    return render_template('audit_predictions.html',
                         bills=bills,
                         policaps=current_user.policaps)
@app.route('/synthetic-consensus')
@login_required
def synthetic_consensus():
    # Get all bills with voting data
    bills = Bill.query.order_by(Bill.voting_deadline.desc()).limit(50).all()
    
    return render_template('synthetic_consensus.html',
                         bills=bills,
                         policaps=current_user.policaps)
{% extends "base.html" %}

{% block content %}
<div class="dashboard">
  <h2>Welcome, {{ current_user.username }}!</h2>
  <div class="policap-balance">
    <h3>Your Policap Balance: {{ policaps }}</h3>
  </div>
  
  <div class="action-cards">
    <div class="card">
      <h3>Answer Questions</h3>
      <p>Earn policaps by answering questions to train your avatar</p>
      <a href="{{ url_for('answer_questions') }}" class="btn">Start Answering</a>
    </div>
    
    <div class="card">
      <h3>Audit Predictions</h3>
      <p>Review and override your avatar's votes on current bills</p>
      <a href="{{ url_for('audit_predictions') }}" class="btn">Audit Votes</a>
    </div>
    
    <div class="card">
      <h3>Synthetic Consensus</h3>
      <p>View the aggregated predictions and voting trends</p>
      <a href="{{ url_for('synthetic_consensus') }}" class="btn">View Consensus</a>
    </div>
  </div>
</div>
{% endblock %}
{% extends "base.html" %}

{% block content %}
<h2>Synthetic Consensus</h2>

<div class="consensus-list">
  {% for bill in bills %}
  <div class="bill-card">
    <h3>{{ bill.title }}</h3>
    <p>{{ bill.summary }}</p>
    
    <div class="vote-visualization">
      <div class="predicted">
        <h4>Predicted Consensus:</h4>
        <div class="bar-container">
          <div class="yes-bar" style="width: {{ bill.predicted_yes }}%">
            {{ bill.predicted_yes|round(1) }}% Yes
          </div>
          <div class="no-bar" style="width: {{ bill.predicted_no }}%">
            {{ bill.predicted_no|round(1) }}% No
          </div>
        </div>
      </div>
      
      <div class="actual">
        <h4>Audited Consensus ({{ bill.audit_rate|round(1) }}% audited):</h4>
        <div class="bar-container">
          <div class="yes-bar" style="width: {{ bill.actual_yes }}%">
            {{ bill.actual_yes|round(1) }}% Yes
          </div>
          <div class="no-bar" style="width: {{ bill.actual_no }}%">
            {{ bill.actual_no|round(1) }}% No
          </div>
        </div>
      </div>
    </div>
    
    <a href="{{ url_for('bill_detail', bill_id=bill.id) }}" class="btn">Details</a>
  </div>
  {% endfor %}
</div>
{% endblock %}
def update_bill_statistics(bill_id):
    bill = Bill.query.get(bill_id)
    votes = UserVote.query.filter_by(bill_id=bill_id).all()
    
    if votes:
        total = len(votes)
        yes_count = sum(1 for v in votes if v.final_vote == 'yes')
        no_count = total - yes_count
        
        bill.actual_yes = (yes_count / total) * 100
        bill.actual_no = (no_count / total) * 100
        
        # Calculate audit rate (percentage of users who voted)
        total_users = User.query.count()
        bill.audit_rate = (total / total_users) * 100
        
        db.session.commit()
from apscheduler.schedulers.background import BackgroundScheduler

def update_all_bill_stats():
    with app.app_context():
        bill_ids = [b.id for b in Bill.query.all()]
        for bill_id in bill_ids:
            update_bill_statistics(bill_id)

scheduler = BackgroundScheduler()
scheduler.add_job(update_all_bill_stats, 'interval', hours=1)
scheduler.start()
