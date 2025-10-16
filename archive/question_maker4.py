import random
from typing import List, Dict

# Canadian political context - refined
POLITICAL_ACTORS = {
    "parties": ["the Liberals", "the Conservatives", "the NDP", "the Bloc Québécois"],
    "leaders": ["Trudeau", "Poilievre", "Singh", "Blanchet"],
    "stakeholders": {
        "economic": ["oil workers", "tech entrepreneurs", "farmers"],
        "geographic": ["Albertans", "Quebecers", "urban renters"],
        "demographic": ["indigenous communities", "new immigrants", "seniors"]
    }
}

VALUE_TENSIONS = [
    ("economic growth", "environmental protection"),
    ("individual freedom", "collective security"),
    ("provincial autonomy", "federal unity"),
    ("traditional values", "social progress"),
    ("free speech", "protection from harm")
]

POLICY_THEMES = [
    "climate policy",
    "housing affordability",
    "healthcare reform",
    "internet regulation",
    "economic stimulus"
]

EMOTIONAL_FRAMING = {
    "positive": ["hopeful", "optimistic", "encouraged"],
    "negative": ["concerned", "skeptical", "alarmed"],
    "intensity": ["slightly", "moderately", "deeply"]
}

def select(items: List[str]) -> str:
    """Selects one random item from a list"""
    return random.choice(items)

def select_stakeholders() -> (str, str):
    """Selects two distinct stakeholder groups"""
    category = select(list(POLITICAL_ACTORS["stakeholders"].keys()))
    groups = POLITICAL_ACTORS["stakeholders"][category]
    return random.sample(groups, 2)

def generate_question() -> str:
    """Generates grammatically correct abstract policy questions"""
    template = select([
        # Tribal alignment templates
        "How would you feel if {party} supported policies that prioritize {value1} over {value2}?",
        "Do you trust {leader}'s approach to balancing {value1} and {value2}?",
        
        # Stakeholder comparison templates
        "Should {group1} receive more policy consideration than {group2} when it comes to {theme}?",
        "Is it fair to ask {group1} to make sacrifices for {theme} that primarily benefits {group2}?",
        
        # Value conflict templates
        "Should Canada prioritize {value1} even if it means less {value2}?",
        "Is protecting {value1} worth limiting {value2} in our {theme} approach?",
        
        # Emotional reaction templates
        "How {intensity} {emotion} are you about recent moves toward {theme}?",
        "When you hear about {theme} debates, do you feel more {positive} or {negative}?"
    ])
    
    value1, value2 = select(VALUE_TENSIONS)
    group1, group2 = select_stakeholders()
    
    return template.format(
        party=select(POLITICAL_ACTORS["parties"]),
        leader=select(POLITICAL_ACTORS["leaders"]),
        group1=group1,
        group2=group2,
        value1=value1,
        value2=value2,
        theme=select(POLICY_THEMES),
        emotion=select(EMOTIONAL_FRAMING["negative"] + EMOTIONAL_FRAMING["positive"]),
        intensity=select(EMOTIONAL_FRAMING["intensity"]),
        positive=select(EMOTIONAL_FRAMING["positive"]),
        negative=select(EMOTIONAL_FRAMING["negative"])
    )

if __name__ == "__main__":
    print("\nGenerated Questions:\n" + "="*40)
    for _ in range(5):
        print(f"- {generate_question()}")
    print()
