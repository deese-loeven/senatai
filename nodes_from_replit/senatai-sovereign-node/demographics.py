"""
Demographic data collection module
Gently asks for optional demographic information to build rich datasets for premium clients
"""

DEMOGRAPHIC_QUESTIONS = [
    {
        'id': 'age_range',
        'question': 'Would you mind sharing your age range? This helps us understand generational perspectives.',
        'type': 'multiple_choice',
        'options': ['18-24', '25-34', '35-44', '45-54', '55-64', '65+', 'Prefer not to say'],
        'skippable': True
    },
    {
        'id': 'gender',
        'question': 'What is your gender identity?',
        'type': 'multiple_choice',
        'options': ['Man', 'Woman', 'Non-binary', 'Prefer to self-describe', 'Prefer not to say'],
        'skippable': True
    },
    {
        'id': 'region',
        'question': 'Which region do you live in? (We never collect exact location)',
        'type': 'multiple_choice',
        'options': ['British Columbia', 'Alberta', 'Saskatchewan', 'Manitoba', 'Ontario', 
                   'Quebec', 'New Brunswick', 'Nova Scotia', 'PEI', 'Newfoundland & Labrador',
                   'Yukon', 'Northwest Territories', 'Nunavut', 'Prefer not to say'],
        'skippable': True
    },
    {
        'id': 'work_experience',
        'question': 'What areas do you have work experience in? (Select all that apply)',
        'type': 'multiple_select',
        'options': ['Healthcare', 'Education', 'Technology', 'Finance', 'Legal', 'Government',
                   'Non-profit', 'Trades', 'Service industry', 'Agriculture', 'Arts & Culture',
                   'Manufacturing', 'Transportation', 'Other', 'Prefer not to say'],
        'skippable': True
    },
    {
        'id': 'expertise_areas',
        'question': 'Do you have particular expertise or lived experience that informs your views on legislation?',
        'type': 'text',
        'placeholder': 'e.g., "Single parent navigating childcare policy", "Small business owner", "Climate scientist", etc.',
        'skippable': True
    },
    {
        'id': 'education_level',
        'question': 'What is your highest level of education?',
        'type': 'multiple_choice',
        'options': ['Some high school', 'High school diploma', 'Some college/university',
                   'College diploma', 'Bachelor\'s degree', 'Master\'s degree', 'Doctoral degree',
                   'Professional degree', 'Prefer not to say'],
        'skippable': True
    }
]


def get_demographic_intro_message():
    """Returns the gentle introduction before asking demographic questions"""
    return {
        'title': 'Help us build better data (optional)',
        'message': """You've answered great questions about legislation! 
        
Now, we'd love to learn a bit about YOU - but only if you're comfortable sharing.

**Why we ask:**
- Researchers, journalists, and policymakers pay for access to demographic breakdowns
- Your optional data helps fund this free platform and your eventual dividends
- The more detailed the data, the more valuable it is to clients

**You can:**
✓ Skip all demographic questions and just keep answering about laws
✓ Provide minimal info (just age range, for example)
✓ Build a rich profile that helps attract premium clients

**Privacy guarantee:**
- We never link your identity to your answers
- Data is only shown in aggregated form to paying clients
- You control what you share""",
        'options': [
            {'label': 'I\'ll answer some demographic questions', 'value': 'answer'},
            {'label': 'Skip demographics, just keep asking about laws', 'value': 'skip'},
            {'label': 'Tell me more about how my data is used', 'value': 'learn_more'}
        ]
    }


def get_data_usage_explanation():
    """Detailed explanation of how demographic data is used"""
    return """
## How Your Demographic Data Creates Value

**Free Tier (Everyone):**
- Sees basic aggregate: "67% support this bill"
- No demographic breakdowns

**$10/mo Student Tier:**
- Sees predicted vs. authenticated votes
- Basic confidence levels

**$100/mo Journalist Tier:**
- Geographic breakdowns (BC vs Ontario)
- Basic demographics (age ranges, gender)

**$1,000/mo Academic Tier:**
- Cross-correlations ("Healthcare workers aged 35-44 in Ontario")
- Detailed demographic slices

**$10,000+ Think Tank & Government Tiers:**
- Fine-grained segmentation
- Values-based groupings ("Voters who prioritize environment AND economy")
- Custom queries

**Your share:**
- You earn Policap for every question you answer
- Policap converts to estimated annual dividend (~50% of balance)
- The richer your data, the more valuable our platform, the higher your dividends

**You're in control:**
- Skip any question
- Provide minimal or maximal information
- Update your demographic info anytime in settings
"""


def save_demographic_responses(user_id, guest_id, responses):
    """Save demographic responses to database"""
    # This will be implemented when we integrate with the database
    pass


def get_next_demographic_question(responses_so_far):
    """Get the next demographic question based on what's been answered"""
    answered_ids = [r['question_id'] for r in responses_so_far]
    
    for q in DEMOGRAPHIC_QUESTIONS:
        if q['id'] not in answered_ids:
            return q
    
    return None  # All questions answered
