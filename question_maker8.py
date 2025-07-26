#!/usr/bin/env python3
import random

# Core themes that appear in legislation (general enough for public understanding)
THEMES = {
    "economic": ["taxation", "economic growth", "small businesses", "inflation", "wages"],
    "social": ["healthcare", "education", "child care", "seniors", "housing"],
    "rights": ["free speech", "privacy", "gun rights", "equality", "indigenous rights"],
    "environment": ["climate change", "energy", "conservation", "pollution", "sustainability"],
    "security": ["public safety", "policing", "cybersecurity", "borders", "defense"]
}

# Political actors/stakeholders
ACTORS = {
    "parties": ["Liberals", "Conservatives", "NDP", "Bloc Québécois", "Green Party"],
    "leaders": ["Trudeau", "Poilievre", "Singh", "Blanchet", "May"],
    "groups": ["small businesses", "unions", "indigenous communities", "seniors", "young families"]
}

# Emotional dimensions to measure
EMOTIONS = {
    "intensity": ["mildly", "somewhat", "very", "extremely"],
    "feelings": ["optimistic", "worried", "angry", "hopeful", "skeptical"],
    "scales": {
        "agreement": ["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"],
        "priority": ["Not important", "Slightly important", "Important", "Very important", "Essential"],
        "trust": ["Not at all", "Slightly", "Moderately", "Very", "Completely"]
    }
}

def generate_theme_question():
    """Generate questions about policy themes"""
    theme_category = random.choice(list(THEMES.keys()))
    theme = random.choice(THEMES[theme_category])
    other_theme = random.choice(THEMES[random.choice([k for k in THEMES if k != theme_category])])
    actor = random.choice(ACTORS["parties"] + ACTORS["leaders"])
    
    templates = [
        f"Should Canada prioritize {theme} even if it means less focus on {other_theme}?",
        f"How {random.choice(EMOTIONS['intensity'])} {random.choice(EMOTIONS['feelings'])} are you about recent moves toward {theme}?",
        f"Does {actor}'s approach to {theme} make you more {random.choice(EMOTIONS['feelings'])} or {random.choice(EMOTIONS['feelings'])}?",
        f"Is protecting {theme} worth limiting {other_theme}?"
    ]
    return random.choice(templates)

def generate_scale_question():
    """Generate questions with scaled response options"""
    theme_category = random.choice(list(THEMES.keys()))
    theme = random.choice(THEMES[theme_category])
    scale_type = random.choice(list(EMOTIONS["scales"].keys()))
    
    question_stems = [
        f"How would you rate the importance of {theme} in Canadian policy?",
        f"To what extent do you agree with prioritizing {theme} over other issues?",
        f"How much do you trust political leaders to handle {theme} effectively?"
    ]
    
    question = random.choice(question_stems)
    return f"{question}\n" + "\n".join([f"{i+1}. {option}" for i, option in enumerate(EMOTIONS["scales"][scale_type])])

def generate_comparison_question():
    """Generate questions comparing two groups/values"""
    theme1, theme2 = random.sample(list(THEMES.keys()), 2)
    group1, group2 = random.sample(ACTORS["groups"], 2)
    
    templates = [
        f"Does {group1} deserve more consideration than {group2} in {random.choice(THEMES[theme1])} policies?",
        f"Is protecting {random.choice(THEMES[theme1])} worth limiting {random.choice(THEMES[theme2])}?",
        f"Should we prioritize {random.choice(THEMES[theme1])} for {group1} over {random.choice(THEMES[theme2])} for {group2}?"
    ]
    return random.choice(templates)

def generate_question_set(num=5):
    """Generate a balanced set of questions"""
    questions = []
    for _ in range(num):
        # Balance question types
        q_type = random.choices(
            [generate_theme_question, generate_scale_question, generate_comparison_question],
            weights=[4, 3, 3],
            k=1
        )[0]
        questions.append(q_type())
    return questions

if __name__ == "__main__":
    print("\nGenerated Public Opinion Questions:")
    print("="*50)
    for i, question in enumerate(generate_question_set(7), 1):
        print(f"\nQ{i}. {question}\n")
EMOTIONS = {
    "intensity": ["mildly", "somewhat", "very", "extremely"],
    "feelings": ["optimistic", "worried", "angry", "hopeful", "skeptical"],
    "scales": {
        "agreement": ["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"],
        "priority": ["Not important", "Slightly important", "Important", "Very important", "Essential"],
        "trust": ["Not at all", "Slightly", "Moderately", "Very", "Completely"]
    }
}THEMES = {
    "economic": ["taxation", "economic growth", "small businesses", "inflation", "wages"],
    "social": ["healthcare", "education", "child care", "seniors", "housing"],
    "rights": ["free speech", "privacy", "gun rights", "equality", "indigenous rights"],
    "environment": ["climate change", "energy", "conservation", "pollution", "sustainability"],
    "security": ["public safety", "policing", "cybersecurity", "borders", "defense"]
}
