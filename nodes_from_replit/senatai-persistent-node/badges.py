"""
Badge system for Senatai
- Production badges: Earned by answering questions (1k-100k Policaps)
- Audit badges: Earned by spending Policaps to audit predictions (way cooler!)
"""

# Policap Production Badges (for answering questions)
PRODUCTION_BADGES = [
    {
        'id': 'producer_1k',
        'name': 'Contributor',
        'threshold': 1000,
        'icon': '🥉',
        'color': '#cd7f32',  # bronze
        'description': '1,000 Policaps earned from answering questions'
    },
    {
        'id': 'producer_5k',
        'name': 'Dedicated Voice',
        'threshold': 5000,
        'icon': '🥈',
        'color': '#c0c0c0',  # silver
        'description': '5,000 Policaps earned from answering questions'
    },
    {
        'id': 'producer_10k',
        'name': 'Power Participant',
        'threshold': 10000,
        'icon': '🥇',
        'color': '#ffd700',  # gold
        'description': '10,000 Policaps earned from answering questions'
    },
    {
        'id': 'producer_25k',
        'name': 'Democracy Champion',
        'threshold': 25000,
        'icon': '💎',
        'color': '#4169e1',  # royal blue
        'description': '25,000 Policaps earned from answering questions'
    },
    {
        'id': 'producer_50k',
        'name': 'Civic Legend',
        'threshold': 50000,
        'icon': '👑',
        'color': '#9370db',  # medium purple
        'description': '50,000 Policaps earned from answering questions'
    },
    {
        'id': 'producer_100k',
        'name': 'Senate Oracle',
        'threshold': 100000,
        'icon': '✨',
        'color': '#ff00ff',  # magenta with special shine
        'description': '100,000 Policaps earned - Elite data producer!',
        'shiny': True
    }
]


def get_audit_badge_thresholds(total_bills):
    """
    Generate audit badges based on actual bill count
    Scale: 1%, 2.5%, 5%, 10%, 20%, 50% of bills audited
    Way cooler than production badges!
    """
    return [
        {
            'id': 'auditor_1pct',
            'name': 'Truth Seeker',
            'threshold': max(1, int(total_bills * 0.01)),
            'icon': '🔍',
            'color': '#00ff00',  # bright green
            'glow': 'soft',
            'description': f'Audited {max(1, int(total_bills * 0.01))} predictions (1% of bills)'
        },
        {
            'id': 'auditor_2.5pct',
            'name': 'Fact Checker',
            'threshold': max(1, int(total_bills * 0.025)),
            'icon': '🎯',
            'color': '#00ffff',  # cyan
            'glow': 'soft',
            'description': f'Audited {max(1, int(total_bills * 0.025))} predictions (2.5% of bills)'
        },
        {
            'id': 'auditor_5pct',
            'name': 'Accuracy Guardian',
            'threshold': max(1, int(total_bills * 0.05)),
            'icon': '⚡',
            'color': '#ffff00',  # yellow
            'glow': 'medium',
            'description': f'Audited {max(1, int(total_bills * 0.05))} predictions (5% of bills)'
        },
        {
            'id': 'auditor_10pct',
            'name': 'Prediction Validator',
            'threshold': max(1, int(total_bills * 0.10)),
            'icon': '🌟',
            'color': '#ff8c00',  # dark orange
            'glow': 'strong',
            'description': f'Audited {max(1, int(total_bills * 0.10))} predictions (10% of bills)'
        },
        {
            'id': 'auditor_20pct',
            'name': 'Algorithm Overseer',
            'threshold': max(1, int(total_bills * 0.20)),
            'icon': '🚀',
            'color': '#ff1493',  # deep pink
            'glow': 'intense',
            'description': f'Audited {max(1, int(total_bills * 0.20))} predictions (20% of bills)'
        },
        {
            'id': 'auditor_50pct',
            'name': 'Supreme Auditor',
            'threshold': max(1, int(total_bills * 0.50)),
            'icon': '🏆',
            'color': '#ffd700',  # gold with rainbow glow
            'glow': 'rainbow',
            'description': f'Audited {max(1, int(total_bills * 0.50))} predictions (50% of bills!)',
            'supreme': True
        }
    ]


def get_user_production_badges(lifetime_policap_earned):
    """
    Get all production badges user has earned
    
    Args:
        lifetime_policap_earned: Total Policaps earned from questions
    
    Returns:
        list: Badges earned, highest first
    """
    earned = [
        badge for badge in PRODUCTION_BADGES 
        if lifetime_policap_earned >= badge['threshold']
    ]
    return sorted(earned, key=lambda x: x['threshold'], reverse=True)


def get_user_audit_badges(audit_count, total_bills):
    """
    Get all audit badges user has earned
    
    Args:
        audit_count: Number of predictions audited
        total_bills: Total bills in system
    
    Returns:
        list: Badges earned, highest first
    """
    thresholds = get_audit_badge_thresholds(total_bills)
    earned = [
        badge for badge in thresholds 
        if audit_count >= badge['threshold']
    ]
    return sorted(earned, key=lambda x: x['threshold'], reverse=True)


def get_next_production_badge(lifetime_policap_earned):
    """Get the next production badge to aim for"""
    for badge in PRODUCTION_BADGES:
        if lifetime_policap_earned < badge['threshold']:
            return {
                'badge': badge,
                'progress': lifetime_policap_earned / badge['threshold'],
                'remaining': badge['threshold'] - lifetime_policap_earned
            }
    return None  # Already have highest badge!


def get_next_audit_badge(audit_count, total_bills):
    """Get the next audit badge to aim for"""
    thresholds = get_audit_badge_thresholds(total_bills)
    for badge in thresholds:
        if audit_count < badge['threshold']:
            return {
                'badge': badge,
                'progress': audit_count / badge['threshold'],
                'remaining': badge['threshold'] - audit_count
            }
    return None  # Already have highest badge!


def calculate_audit_spend_limit(bill_id, user_id, cursor):
    """
    Calculate how much a user can spend on auditing this bill
    Rules:
    - Anyone can spend within +/- 2 limit
    - If they've spent + then -, we need to ask what changed
    - If at limit, can only spend in opposite direction
    
    Returns:
        dict: {
            'can_confirm': bool,
            'can_veto': bool,
            'confirm_limit': int (how many more confirms allowed),
            'veto_limit': int (how many more vetos allowed),
            'total_confirms': int,
            'total_vetos': int,
            'switched_position': bool (did they go from + to - or vice versa%s)
        }
    """
    # Get user's audit history for this bill
    cursor.execute('''
        SELECT spending_type, policap_spent 
        FROM policap_spending 
        WHERE user_id = %s AND bill_id = %s 
        ORDER BY timestamp ASC
    ''', (user_id, bill_id))
    
    audits = cursor.fetchall()
    
    total_confirms = sum(1 for a in audits if a[0] == 'confirm_prediction')
    total_vetos = sum(1 for a in audits if a[0] == 'veto_prediction')
    
    # Check for position switches
    switched = False
    if len(audits) >= 2:
        types = [a[0] for a in audits]
        # Look for confirm → veto or veto → confirm pattern
        for i in range(len(types) - 1):
            if (types[i] == 'confirm_prediction' and types[i+1] == 'veto_prediction') or \
               (types[i] == 'veto_prediction' and types[i+1] == 'confirm_prediction'):
                switched = True
                break
    
    # Calculate limits (max 2 in each direction)
    confirm_limit = 2 - total_confirms
    veto_limit = 2 - total_vetos
    
    # If at limit in one direction, can still spend in opposite
    can_confirm = confirm_limit > 0 or total_vetos > 0
    can_veto = veto_limit > 0 or total_confirms > 0
    
    return {
        'can_confirm': can_confirm,
        'can_veto': can_veto,
        'confirm_limit': max(0, confirm_limit),
        'veto_limit': max(0, veto_limit),
        'total_confirms': total_confirms,
        'total_vetos': total_vetos,
        'switched_position': switched
    }
