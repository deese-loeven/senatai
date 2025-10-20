import re

with open('policap_rewards.py', 'r') as f:
    content = f.read()

# Fix the specific get_daily_stats function
old_function = '''def get_daily_stats(cursor, user_id, today=None):
    """Get today's question and vote counts for a user"""
    if today is None:
        today = date.today()
    
    cursor.execute('''
        SELECT question_count, vote_count 
        FROM daily_question_count 
        WHERE user_id = ? AND activity_date = ?
    ''', (user_id, today))'''

new_function = '''def get_daily_stats(cursor, user_id, today=None):
    """Get today's question and vote counts for a user"""
    if today is None:
        today = date.today()
    
    cursor.execute('''
        SELECT question_count, vote_count 
        FROM daily_question_count 
        WHERE user_id = %s AND activity_date = %s
    ''', (user_id, today))'''

content = content.replace(old_function, new_function)

# Also fix the PostgreSQL version if it exists
old_postgres = '''def get_daily_stats_postgres(cursor, user_id, today=None):
    """PostgreSQL version of get_daily_stats"""
    if today is None:
        today = date.today()
    
    cursor.execute('''
        SELECT question_count, vote_count 
        FROM daily_question_count 
        WHERE user_id = ? AND activity_date = ?
    ''', (user_id, today))'''

new_postgres = '''def get_daily_stats_postgres(cursor, user_id, today=None):
    """PostgreSQL version of get_daily_stats"""
    if today is None:
        today = date.today()
    
    cursor.execute('''
        SELECT question_count, vote_count 
        FROM daily_question_count 
        WHERE user_id = %s AND activity_date = %s
    ''', (user_id, today))'''

content = content.replace(old_postgres, new_postgres)

with open('policap_rewards.py', 'w') as f:
    f.write(content)

print("✅ Fixed specific SQL functions in policap_rewards.py")
