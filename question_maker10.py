#!/usr/bin/env python3
import random
import sys
from functools import wraps
import time

# Safety feature - timeout after 1 second
def timeout(seconds=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            if time.time() - start > seconds:
                raise TimeoutError("Function took too long")
            return result
        return wrapper
    return decorator

# Expanded question components
THEMES = {
    "economic": ["taxation", "economic growth", "small business support", 
                "inflation control", "wage policies"],
    "social": ["healthcare access", "education funding", "child care programs",
              "senior benefits", "housing affordability"],
    "rights": ["free speech protections", "digital privacy", "gun ownership rights",
              "gender equality", "indigenous rights"],
    "environment": ["climate change", "clean energy", "wildlife conservation",
                   "pollution reduction", "sustainable development"]
}

ACTORS = {
    "parties": ["Liberal", "Conservative", "NDP", "Bloc Québécois", "Green"],
    "leaders": ["Trudeau", "Poilievre", "Singh", "Blanchet", "May"],
    "groups": ["small business owners", "union workers", "indigenous communities", 
              "senior citizens", "young families"]
}

EMOTIONS = {
    "intensity": ["slightly", "moderately", "very", "extremely"],
    "feelings": ["optimistic", "concerned", "angry", "hopeful", "skeptical"]
}

@timeout()
def generate_theme_question():
    theme1, theme2 = random.sample([t for sublist in THEMES.values() for t in sublist], 2)
    templates = [
        f"Should Canada prioritize {theme1} over {theme2}?",
        f"How {random.choice(EMOTIONS['intensity'])} {random.choice(EMOTIONS['feelings'])} are you about {theme1}?",
        f"Is improving {theme1} worth potential trade-offs in {theme2}?"
    ]
    return random.choice(templates)

@timeout()
def generate_comparison_question():
    group1, group2 = random.sample(ACTORS['groups'], 2)
    theme = random.choice([t for sublist in THEMES.values() for t in sublist])
    return f"Should {group1} receive more support than {group2} for {theme}?"

@timeout()
def generate_scaled_question():
    theme = random.choice([t for sublist in THEMES.values() for t in sublist])
    return f"Rate your agreement: '{theme} should be a top government priority'\n" \
           "1. Strongly disagree\n2. Disagree\n3. Neutral\n4. Agree\n5. Strongly agree"

def generate_question():
    question_types = [
        generate_theme_question,
        generate_comparison_question,
        generate_scaled_question
    ]
    return random.choice(question_types)()

if __name__ == "__main__":
    try:
        print("New Survey Question:")
        print("="*40)
        print(generate_question())
    except TimeoutError:
        print("Error generating question", file=sys.stderr)
        sys.exit(1)
