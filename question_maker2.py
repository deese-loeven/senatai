import random
from typing import Optional

# Political context for Canadian politics
PARTIES = ["Trudeau's Liberals", "Poilievre's Conservatives", "the NDP", "Bloc Québécois"]
VALUES = ["economic growth", "climate action", "personal freedom", "social justice"] 
GROUPS = ["oil workers", "young families", "indigenous communities", "small businesses"]
EMOTIONS = ["angry", "hopeful", "skeptical", "enthusiastic"]

# Question templates organized by predictive dimension
TEMPLATES = {
    'tribal': [
        "If {party} strongly supported '{bill_title}', how would that affect your view of it?",
        "Does '{bill_title}' sound like something {party} would propose?",
        "Would you be more likely to support '{bill_title}' if you knew {party} opposed it?"
    ],
    'values': [
        "Should Canada prioritize {value} through laws like '{bill_title}'?",
        "Does '{bill_title}' seem to favor {group} over others?",
        "Is {value} worth potential tradeoffs from '{bill_title}'?"
    ],
    'emotional': [
        "How {emotion} does '{bill_title}' make you feel?",
        "On a scale of 1-10, how strongly do you react to bills like '{bill_title}'?",
        "Does '{bill_title}' make you more worried or optimistic about Canada's future?"
    ]
}

def generate_question(bill_title: str, focus: Optional[str] = None) -> str:
    """
    Generates abstract voting-intent questions from bill titles.
    
    Args:
        bill_title: The title of the bill (e.g., "Bill C-123: Climate Accountability Act")
        focus: Optional filter ('tribal', 'values', 'emotional')
    
    Returns:
        An abstract voting prediction question
    """
    # Select question type
    question_type = focus if focus in TEMPLATES else random.choice(list(TEMPLATES.keys()))
    
    # Get template and fill placeholders
    template = random.choice(TEMPLATES[question_type])
    return template.format(
        bill_title=bill_title,
        party=random.choice(PARTIES),
        value=random.choice(VALUES),
        group=random.choice(GROUPS),
        emotion=random.choice(EMOTIONS)
    )

# Example usage
if __name__ == "__main__":
    bills = [
        "Bill C-234: Carbon Tax Relief Act",
        "Bill S-245: Online Harms Protection Act", 
        "Bill C-35: Child Care Expansion Act"
    ]
    
    for bill in bills:
        print(generate_question(bill))
        print(generate_question(bill, focus='emotional'))
        print()
