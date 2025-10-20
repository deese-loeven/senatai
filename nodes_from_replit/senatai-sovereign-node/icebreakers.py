import random

ICEBREAKERS = [
    # Civic/Voting Themed
    "Vote booth open",
    "Democracy desk accepting visitors",
    "Your representative is listening (allegedly)",
    "Polling station: open 24/7",
    "Ballot box ready for your thoughts",
    "Town hall in session",
    "Public comment period: always open",
    "The floor is yours",
    "Your turn to speak",
    "Democracy hotline: connected",
    
    # Direct/Blunt
    "Let 'em know what you really think",
    "Say what you actually mean",
    "No filter needed here",
    "Speak your mind",
    "Tell it like it is",
    "Get it off your chest",
    "What's really bothering you?",
    "Unload whatever's on your mind",
    "No bullshit zone",
    "Real talk time",
    
    # Complaints/Venting Themed
    "Complaints department is open",
    "Grievance office accepting submissions",
    "Vent session: now live",
    "Complaint box: unlocked",
    "Problems? We're listening",
    "What's broken today?",
    "Suggestion box (for angry suggestions)",
    "Customer feedback (government edition)",
    "Comment card for democracy",
    "What needs fixing?",
    
    # Question/Curiosity Driven
    "What's on your mind?",
    "Penny for your thoughts?",
    "What matters to you?",
    "What keeps you up at night?",
    "What would you change?",
    "If you could fix one thing…",
    "What's your take?",
    "Got something to say?",
    "What bugs you about this country?",
    "What should we be talking about?",
    
    # Frustrated/Relatable
    "Rent too high? We're listening",
    "Frustration station: all aboard",
    "Mad as hell? Type it out",
    "Something pissing you off?",
    "System broken? Tell us how",
    "Politicians not listening? We are",
    "Fed up? You're not alone",
    "What's grinding your gears?",
    "Tired of being ignored? Not here",
    "Rage room (text edition)"
]


def get_random_icebreaker():
    """Get a random icebreaker message"""
    return random.choice(ICEBREAKERS)


def get_icebreaker_by_vibe(vibe='casual'):
    """Get an icebreaker matching a specific vibe"""
    vibes = {
        'professional': ICEBREAKERS[0:10],
        'casual': ICEBREAKERS[30:40],
        'spicy': ICEBREAKERS[10:20] + ICEBREAKERS[40:50],
        'empathetic': ICEBREAKERS[20:30]
    }
    
    options = vibes.get(vibe, ICEBREAKERS)
    return random.choice(options)
