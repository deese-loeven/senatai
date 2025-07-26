import random
from typing import Dict, List

# Political archetypes - Canadian edition
POLITICAL_ACTORS = {
    "parties": ["Liberals", "Conservatives", "NDP", "Bloc Québécois"],
    "leaders": ["Trudeau", "Poilievre", "Singh", "Blanchet"],
    "groups": ["oil workers", "urban renters", "indigenous communities", "small businesses"]
}

# Value tensions in Canadian politics
VALUE_CONFLICTS = [
    ("economic growth", "environmental protection"),
    ("individual freedom", "collective security"),
    ("provincial rights", "federal authority"),
    ("traditional values", "social progress")
]

# Emotional triggers
EMOTIONAL_FRAMING = {
    "positive": ["hopeful about", "optimistic that", "excited by"],
    "negative": ["angry about", "worried that", "fearful of"],
    "intensity": ["mildly", "somewhat", "deeply"]
}

# Common legislative themes (these would normally come from bill analysis)
THEMES = [
    "carbon pricing",
    "housing affordability",
    "health care funding",
    "online speech regulation",
    "child care expansion"
]

def generate_theme_question() -> str:
    """Generates abstract voting-intent questions based on political themes"""
    conflict = random.choice(VALUE_CONFLICTS)
    actor = random.choice(POLITICAL_ACTORS["parties"])
    group1, group2 = random.sample(POLITICAL_ACTORS["groups"], 2)
    emotion = random.choice(list(EMOTIONAL_FRAMING["positive"] + EMOTIONAL_FRAMING["negative"]))
    
    templates = [
        # Tribal alignment questions
        f"How would you feel if {{party}} compromised on {{value1}} to achieve {{value2}}?",
        f"Does {{group1}} deserve more consideration than {{group2}} in {{theme}} policies?",
        
        # Value tradeoff questions
        f"Should Canada prioritize {{value1}} over {{value2}}?",
        f"Is {{value1}} worth sacrificing some {{value2}} for?",
        
        # Emotional reaction questions
        f"How {{intensity}} {{emotion}} are you about {{theme}} legislation?",
        f"Does the debate around {{theme}} make you more {{positive}} or {{negative}}?"
    ]
    
    return random.choice(templates).format(
        party=actor,
        group1=group1,
        group2=group2,
        value1=conflict[0],
        value2=conflict[1],
        theme=random.choice(THEMES),
        emotion=emotion,
        intensity=random.choice(EMOTIONAL_FRAMING["intensity"]),
        positive=random.choice(EMOTIONAL_FRAMING["positive"]),
        negative=random.choice(EMOTIONAL_FRAMING["negative"])
    )

if __name__ == "__main__":
    for _ in range(5):  # Generate 5 sample questions
        print(generate_theme_question())
        print()
