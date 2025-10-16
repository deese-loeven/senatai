import random

def generate_emotional_clause_questions(bill_name, clauses):
    """
    Generates questions that gauge emotional responses to specific clauses in a bill.

    Args:
        bill_name (str): The name of the bill.
        clauses (list of str): A list of clauses from the bill.

    Returns:
        list of str: A list of generated questions.
    """

    questions = []
    emotions = [
        "angry", "sad", "happy", "excited", "anxious", "hopeful",
        "fearful", "frustrated", "relieved", "disappointed", "indifferent",
        "surprised", "skeptical", "optimistic", "worried", "outraged"
    ]
    intensities = [
        "slightly", "moderately", "very", "extremely", "somewhat", "a little",
        "not at all", "quite", "rather", "intensely", "mildly"
    ]
    scales = [
        "on a scale of 1-10",
        "to what extent",
        "how deeply",
        "how intensely"
    ]

    for clause in clauses:
        question_type = random.randint(1, 3)

        if question_type == 1:
            emotion = random.choice(emotions)
            intensity = random.choice(intensities)
            questions.append(f"How {intensity} {emotion} does the clause '{clause}' from '{bill_name}' make you feel?")

        elif question_type == 2:
            emotion = random.choice(emotions)
            scale = random.choice(scales)
            questions.append(f"{scale}, how {emotion} does the clause '{clause}' from '{bill_name}' make you feel?")

        else:
            emotion1 = random.choice(emotions)
            emotion2 = random.choice(emotions)
            if random.random() < 0.5:
              questions.append(f"Does the clause '{clause}' from '{bill_name}' make you feel more {emotion1} or {emotion2}?")
            else:
              questions.append(f"How does the clause '{clause}' from '{bill_name}' make you feel, in terms of {emotion1} and {emotion2}?")

    return questions

# Example usage:
bill = "Bill C-21: Firearms Act"
bill_clauses = [
    "Restricts the sale of certain handguns.",
    "Imposes stricter penalties for gun smuggling.",
    "Provides funding for community-based violence prevention programs.",
    "Expands background checks for gun purchases.",
    "Defines certain replica firearms as prohibited weapons."
]

generated_questions = generate_emotional_clause_questions(bill, bill_clauses)

print("Generated Questions:")
print("========================================")
for question in generated_questions:
    print(f"- {question}")
