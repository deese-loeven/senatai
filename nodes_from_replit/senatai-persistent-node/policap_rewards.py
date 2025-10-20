"""
Policap reward calculation system
Implements diminishing returns to encourage engagement while preventing gaming
"""

from datetime import date


def calculate_question_reward(daily_question_count):
    """
    Calculate Policap reward for answering a question based on daily count
    
    Rate schedule:
    - Questions 1-100/day: 1.0 Policap per answer
    - Questions 101-250/day: Diminishes from 1.0 → 0.01 Policaps (linear)
    - Questions 250+/day: 0.001 Policaps per answer
    
    Args:
        daily_question_count: Number of questions already answered today (before this one)
    
    Returns:
        float: Policap reward for this question
    """
    # This will be question number (count + 1)
    question_number = daily_question_count + 1
    
    # First 100 questions: Full reward
    if question_number <= 100:
        return 1.0
    
    # Questions 101-250: Diminishing returns (linear interpolation)
    elif question_number <= 250:
        # At question 101: 1.0 Policap
        # At question 250: 0.01 Policap
        # Linear decline over 150 questions
        progress = (question_number - 100) / 150  # 0.0 at Q101, 1.0 at Q250
        reward = 1.0 - (progress * 0.99)  # 1.0 → 0.01
        return round(reward, 4)
    
    # Questions 250+: Minimal reward
    else:
        return 0.001


def calculate_voting_reward(daily_vote_count):
    """
    Calculate Policap reward for voting on legislation (original system)
    
    Args:
        daily_vote_count: Number of votes already cast today (before this one)
    
    Returns:
        float: Policap reward for this vote
    """
    vote_number = daily_vote_count + 1
    
    if vote_number <= 10:
        return 1.0
    else:
        # Diminishing returns after 10 votes
        diminishing_factor = 1.0 / (vote_number - 8)
        return max(0.1, diminishing_factor)


def get_daily_stats(cursor, user_id, today=None):
    """
    Get user's daily question and vote counts
    
    Args:
        cursor: Database cursor
        user_id: User ID
        today: Date to check (defaults to today)
    
    Returns:
        dict: {'questions': int, 'votes': int}
    """
    if today is None:
        today = date.today()
    
    # Try to get existing daily stats
    cursor.execute('''
        SELECT question_count, vote_count 
        FROM daily_question_count 
        WHERE user_id = %s AND activity_date = %s
    ''', (user_id, today))
    
    result = cursor.fetchone()
    
    if result:
        return {'questions': result[0], 'votes': result[1]}
    else:
        # Initialize today's record
        cursor.execute('''
            INSERT INTO daily_question_count (user_id, activity_date, question_count, vote_count)
            VALUES (?, ?, 0, 0)
        ''', (user_id, today))
        return {'questions': 0, 'votes': 0}


def get_daily_stats_postgres(cursor, user_id, today=None):
    """
    PostgreSQL version of get_daily_stats
    """
    if today is None:
        today = date.today()
    
    cursor.execute('''
        SELECT question_count, vote_count 
        FROM daily_question_count 
        WHERE senatair_id = %s AND activity_date = %s
    ''', (user_id, today))
    
    result = cursor.fetchone()
    
    if result:
        return {'questions': result[0], 'votes': result[1]}
    else:
        # Initialize today's record
        cursor.execute('''
            INSERT INTO daily_question_count (senatair_id, activity_date, question_count, vote_count)
            VALUES (%s, %s, 0, 0)
        ''', (user_id, today))
        return {'questions': 0, 'votes': 0}


def award_question_policap(cursor, user_id, is_postgres=False):
    """
    Award Policap for answering a question and update daily count
    
    Args:
        cursor: Database cursor (with active transaction)
        user_id: User ID
        is_postgres: Whether using PostgreSQL (vs SQLite)
    
    Returns:
        float: Policap amount awarded
    """
    today = date.today()
    
    # Get current daily stats
    if is_postgres:
        stats = get_daily_stats_postgres(cursor, user_id, today)
    else:
        stats = get_daily_stats(cursor, user_id, today)
    
    # Calculate reward based on current count
    reward = calculate_question_reward(stats['questions'])
    
    # Update question count
    if is_postgres:
        cursor.execute('''
            UPDATE daily_question_count 
            SET question_count = question_count + 1
            WHERE senatair_id = %s AND activity_date = %s
        ''', (user_id, today))
        
        # Update user balance
        cursor.execute('''
            UPDATE senatairs 
            SET policap_balance = policap_balance + %s
            WHERE id = %s
        ''', (reward, user_id))
        
        # Record transaction
        cursor.execute('''
            INSERT INTO policap_transactions (senatair_id, amount, transaction_type, description)
            VALUES (%s, %s, %s, %s)
        ''', (user_id, reward, 'question_reward', f'Question #{stats["questions"] + 1} today'))
    else:
        cursor.execute('''
            UPDATE daily_question_count 
            SET question_count = question_count + 1
            WHERE user_id = %s AND activity_date = %s
        ''', (user_id, today))
        
        # Update user balance and lifetime earnings
        cursor.execute('''
            UPDATE users 
            SET policap_balance = policap_balance + ?,
                lifetime_policap_earned = lifetime_policap_earned + ?
            WHERE id = %s
        ''', (reward, reward, user_id))
        
        # Record transaction
        cursor.execute('''
            INSERT INTO policap_transactions (user_id, amount, transaction_type, description)
            VALUES (?, ?, ?, ?)
        ''', (user_id, reward, 'question_reward', f'Question #{stats["questions"] + 1} today'))
    
    return reward


def get_reward_preview(daily_question_count):
    """
    Get a preview of the next few rewards without awarding them
    
    Args:
        daily_question_count: Current daily question count
    
    Returns:
        list: Next 5 rewards [current, +1, +2, +3, +4]
    """
    return [
        calculate_question_reward(daily_question_count + i)
        for i in range(5)
    ]
