import random
import hashlib # Critical for the audit/receipt hash

# ... (EMOTIONS, INTENSITIES, VALUES_PAIRS, etc., remain unchanged) ...

# --- UTILITY FUNCTION FOR HASHING (UPDATED) ---
def generate_question_hash(question_text, options, context_id=None):
    """
    Creates a unique SHA-256 hash for all questions for auditing/tracking.
    
    If context_id is provided (e.g., bill_id), it makes the hash specific to that context, 
    perfect for bill-specific/non-reusable questions (the auditable receipt).
    If context_id is None, the hash is based only on text/options, creating a globally 
    unique ID for reusable questions (the permanent repository key).
    """
    # Use context_id instead of just bill_id to generalize for ALL question types
    data = f"{question_text}|{options if options else ''}|{context_id if context_id else ''}"
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

# ... (All individual question generators remain unchanged) ...

# ... (PERMANENT_GENERATORS and BILL_SPECIFIC_GENERATORS lists remain unchanged) ...


# --- MAIN GENERATOR FUNCTION (UPDATED LOGIC) ---
def generate_questions_for_bill(bill_id, bill_title, bill_summary, category='General', num_questions=5):
    """
    Generates questions, applying the hash to ALL questions for Policap audit/reward, 
    but varies the hash input based on reusability.
    Returns two lists: (permanent_questions, bill_specific_questions)
    """
    
    # Calculate 70/30 split
    num_permanent = round(num_questions * 0.7)
    num_bill_specific = num_questions - num_permanent

    permanent_questions = []
    bill_specific_questions = []

    # 1. Generate Permanent Questions (70% - Reusable Principles)
    p_generators = random.sample(PERMANENT_GENERATORS, min(num_permanent, len(PERMANENT_GENERATORS)))
    
    for generator in p_generators:
        try:
            question = generator(bill_title, bill_id, category) 
            
            # CRITICAL: HASHING FOR REUSABILITY (context_id=None)
            q_hash = generate_question_hash(question['text'], question['options'], context_id=None)
            question['question_hash'] = q_hash
            
            question['bill_id'] = bill_id
            question['module_name'] = 'Sophisticated Question Generator v1.0 (Permanent)'
            permanent_questions.append(question)
        except Exception as e:
            print(f"Error generating permanent question: {e}")
            continue

    # 2. Generate Bill-Specific Questions (30% - Auditable Receipt)
    b_generators = random.sample(BILL_SPECIFIC_GENERATORS, min(num_bill_specific, len(BILL_SPECIFIC_GENERATORS)))
    
    for generator in b_generators:
        try:
            question = generator(bill_title, bill_id, category)
            
            # CRITICAL: HASHING FOR AUDIT RECEIPT (context_id=bill_id)
            # This hash is unique to the question + the specific bill/context
            q_hash = generate_question_hash(question['text'], question['options'], context_id=bill_id) 
            question['question_hash'] = q_hash
            
            question['bill_id'] = bill_id
            question['module_name'] = 'Sophisticated Question Generator v1.0 (Specific)'
            bill_specific_questions.append(question)
        except Exception as e:
            print(f"Error generating specific question: {e}")
            continue
            
    return permanent_questions, bill_specific_questions

import random

EMOTIONS = [
    'hopeful', 'angry', 'worried', 'skeptical', 'fearful', 'optimistic', 
    'excited', 'disappointed', 'relieved', 'outraged', 'enthusiastic', 
    'anxious', 'sad', 'indifferent'
]

INTENSITIES = [
    'very', 'quite', 'extremely', 'deeply', 'intensely', 'moderately', 
    'slightly', 'somewhat', 'mildly'
]

VALUES_PAIRS = [
    ('economic growth', 'environmental protection'),
    ('individual freedom', 'collective security'),
    ('free speech', 'protection from harm'),
    ('traditional values', 'social progress'),
    ('provincial autonomy', 'federal unity'),
    ('personal privacy', 'public safety')
]

PARTIES = [
    "Liberals",
    'Conservatives',
    'NDP',
    'Bloc Québécois',
    'Green Party'
]

GROUPS = [
    'young families',
    'seniors',
    'oil workers',
    'indigenous communities',
    'new immigrants',
    'urban renters',
    'rural communities',
    'small business owners'
]

POLICY_THEMES = {
    'Environment': ['climate policy', 'carbon pricing', 'environmental protection'],
    'Economy': ['economic stimulus', 'fiscal policy', 'taxation'],
    'Social Services': ['health care funding', 'social programs', 'welfare'],
    'Media': ['internet regulation', 'online speech regulation', 'platform regulation'],
    'Privacy': ['data protection', 'privacy rights', 'surveillance'],
    'Labor': ['workers\' rights', 'employment law', 'pensions'],
}


def generate_emotional_reaction_question(bill_title, bill_id):
    emotion = random.choice(EMOTIONS)
    templates = [
        f"How {emotion} does '{bill_title}' make you feel?",
        f"To what extent does '{bill_title}' make you feel {emotion}?",
        f"Does '{bill_title}' make you more {emotion} or indifferent?",
    ]
    return {
        'type': 'emotional_reaction',
        'text': random.choice(templates),
        'options': None
    }


def generate_emotional_scale_question(bill_title, bill_id):
    intensity = random.choice(INTENSITIES)
    emotion = random.choice(EMOTIONS)
    templates = [
        f"How {intensity} {emotion} are you about '{bill_title}'?",
        f"On a scale of 1-10, how {emotion} does '{bill_title}' make you feel?",
    ]
    return {
        'type': 'emotional_scale',
        'text': random.choice(templates),
        'options': None
    }


def generate_values_tradeoff_question(bill_title, bill_id, category='General'):
    value_a, value_b = random.choice(VALUES_PAIRS)
    
    theme = POLICY_THEMES.get(category, ['policy'])[0] if category in POLICY_THEMES else 'policy'
    
    templates = [
        f"Is protecting {value_a} worth limiting {value_b} in our {theme} approach?",
        f"Should Canada prioritize {value_a} even if it means less {value_b}?",
        f"Would you accept reduced {value_b} to strengthen {value_a} in '{bill_title}'?",
    ]
    return {
        'type': 'values_tradeoff',
        'text': random.choice(templates),
        'options': None
    }


def generate_partisan_framing_question(bill_title, bill_id):
    party = random.choice(PARTIES)
    support_oppose = random.choice(['supported', 'opposed'])
    
    templates = [
        f"Would you be more likely to support '{bill_title}' if you knew {party} {support_oppose} it?",
        f"If {party} strongly {support_oppose} '{bill_title}', how would that affect your view of it?",
        f"How would you feel if {party} {support_oppose} '{bill_title}'?",
    ]
    return {
        'type': 'partisan_framing',
        'text': random.choice(templates),
        'options': None
    }


def generate_fairness_question(bill_title, bill_id, category='General'):
    group_a, group_b = random.sample(GROUPS, 2)
    theme = POLICY_THEMES.get(category, ['policy'])[0] if category in POLICY_THEMES else 'policy'
    
    templates = [
        f"Does '{bill_title}' seem to favor {group_a} over {group_b}?",
        f"Should {group_a} receive more policy consideration than {group_b} when it comes to '{bill_title}'?",
        f"Does {group_a} deserve more consideration than {group_b} in {theme} policies like this?",
    ]
    return {
        'type': 'fairness',
        'text': random.choice(templates),
        'options': None
    }


def generate_trust_question(bill_title, bill_id):
    value_a, value_b = random.choice(VALUES_PAIRS)
    party = random.choice(PARTIES[:3])
    
    templates = [
        f"Do you trust {party}'s approach to balancing {value_a} and {value_b}?",
        f"How much confidence do you have in {party} handling issues like '{bill_title}'?",
    ]
    return {
        'type': 'trust',
        'text': random.choice(templates),
        'options': None
    }


def generate_optimism_worry_question(bill_title, bill_id, category='General'):
    theme = POLICY_THEMES.get(category, ['policy'])[0] if category in POLICY_THEMES else 'legislation'
    
    templates = [
        f"Does '{bill_title}' make you more worried or optimistic about Canada's future?",
        f"When you hear about {theme} debates, do you feel more encouraged or concerned?",
        f"Does the debate around {theme} make you more excited or worried?",
    ]
    return {
        'type': 'optimism_worry',
        'text': random.choice(templates),
        'options': None
    }


def generate_intensity_scale_question(bill_title, bill_id):
    templates = [
        f"On a scale of 1-10, how strongly do you react to bills like '{bill_title}'?",
        f"How important is this issue to you personally (1-10)?",
        f"Rate your level of concern about '{bill_title}' from 1 (not concerned) to 10 (extremely concerned).",
    ]
    return {
        'type': 'intensity_scale',
        'text': random.choice(templates),
        'options': None
    }


def generate_principle_question(bill_title, bill_id, category='General'):
    value_a, value_b = random.choice(VALUES_PAIRS)
    
    templates = [
        f"Is {value_a} worth sacrificing some {value_b} for?",
        f"Should Canada always prioritize {value_a}, even at the expense of {value_b}?",
    ]
    return {
        'type': 'principle',
        'text': random.choice(templates),
        'options': None
    }


def generate_compromise_question(bill_title, bill_id):
    party = random.choice(PARTIES[:4])
    value_a, value_b = random.choice(VALUES_PAIRS)
    
    template = f"How would you feel if {party} compromised on {value_a} to achieve {value_b}?"
    return {
        'type': 'compromise',
        'text': template,
        'options': None
    }


def generate_comprehension_question(bill_title, bill_id, category='General'):
    templates = [
        f"What do you think is the primary goal of '{bill_title}'?",
        f"Based on the title and summary, which group would be most affected by '{bill_title}'?",
        f"In your own words, what problem is '{bill_title}' trying to solve?",
        f"Who do you think would benefit most from '{bill_title}'?",
    ]
    return {
        'type': 'comprehension',
        'text': random.choice(templates),
        'options': None
    }


def generate_edge_case_question(bill_title, bill_id, category='General'):
    scenarios = [
        ('rural communities', 'urban areas'),
        ('small businesses', 'large corporations'),
        ('young workers', 'retirees'),
        ('English-speaking provinces', 'Quebec'),
        ('coastal regions', 'prairie provinces'),
    ]
    
    scenario_a, scenario_b = random.choice(scenarios)
    
    templates = [
        f"How might '{bill_title}' affect {scenario_a} differently than {scenario_b}?",
        f"What unintended consequences might arise from implementing '{bill_title}'?",
        f"Can you think of a situation where '{bill_title}' might not work as intended?",
        f"How could '{bill_title}' create different outcomes for {scenario_a} vs. {scenario_b}?",
    ]
    return {
        'type': 'edge_case',
        'text': random.choice(templates),
        'options': None
    }


def generate_clause_emotional_question(bill_title, bill_id, clause_text):
    emotion = random.choice(EMOTIONS)
    intensity = random.choice(INTENSITIES)
    
    emotion_responses = {
        'anger': [
            'Outraged by this provision',
            'Frustrated but understand the intent',
            'Indifferent to this clause',
            'Relieved that action is being taken'
        ],
        'anxiety': [
            'Worried about potential consequences',
            'Anxious about implementation',
            'Unconcerned about the changes',
            'Hopeful it will be effective'
        ],
        'hope': [
            'Very optimistic about this',
            'Slightly hopeful, but skeptical',
            'No hope this will help',
            'Cautiously optimistic'
        ],
        'fear': [
            'Fearful of negative impacts',
            'Concerned about unintended effects',
            'Not fearful at all',
            'Fearful it won\'t be effective'
        ]
    }
    
    emotion_category = random.choice(['anger', 'anxiety', 'hope', 'fear'])
    options_list = emotion_responses[emotion_category]
    
    question_text = f"How does the clause '{clause_text[:80]}...' from '{bill_title}' make you feel in terms of {emotion_category}?"
    
    return {
        'type': 'clause_emotional_mc',
        'text': question_text,
        'options': '||'.join([f"{i+1}. {opt}" for i, opt in enumerate(options_list)]),
        'clause_text': clause_text
    }


QUESTION_GENERATORS = [
    generate_emotional_reaction_question,
    generate_emotional_scale_question,
    generate_values_tradeoff_question,
    generate_partisan_framing_question,
    generate_fairness_question,
    generate_trust_question,
    generate_optimism_worry_question,
    generate_intensity_scale_question,
    generate_principle_question,
    generate_compromise_question,
    generate_comprehension_question,
    generate_edge_case_question,
]


def generate_questions_for_bill(bill_id, bill_title, bill_summary, category='General', num_questions=5):
    questions = []
    
    generators = random.sample(QUESTION_GENERATORS, min(num_questions, len(QUESTION_GENERATORS)))
    
    category_aware_generators = [
        generate_values_tradeoff_question,
        generate_fairness_question,
        generate_optimism_worry_question,
        generate_comprehension_question,
        generate_edge_case_question
    ]
    
    for generator in generators:
        try:
            if generator in category_aware_generators:
                question = generator(bill_title, bill_id, category)
            else:
                question = generator(bill_title, bill_id)
            
            question['bill_id'] = bill_id
            question['module_name'] = 'Sophisticated Question Generator v1.0'
            questions.append(question)
        except Exception as e:
            print(f"Error generating question: {e}")
            continue
    
    return questions


def generate_all_question_types_for_bill(bill_id, bill_title, bill_summary, category='General'):
    questions = []
    
    questions.append(generate_emotional_reaction_question(bill_title, bill_id))
    questions.append(generate_values_tradeoff_question(bill_title, bill_id, category))
    questions.append(generate_partisan_framing_question(bill_title, bill_id))
    questions.append(generate_fairness_question(bill_title, bill_id, category))
    questions.append(generate_optimism_worry_question(bill_title, bill_id, category))
    
    for q in questions:
        q['bill_id'] = bill_id
        q['module_name'] = 'Sophisticated Question Generator v1.0'
    
    return questions
