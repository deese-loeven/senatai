import random

def generate_emotional_clause_questions_with_choices(bill_name, clause, choices):
    """
    Generates multiple-choice questions about emotional responses to a specific clause.

    Args:
        bill_name (str): The name of the bill.
        clause (str): The clause from the bill.
        choices (dict): A dictionary of emotions and their corresponding multiple-choice options.

    Returns:
        list of str: A list of generated questions with choices.
    """

    questions = []
    emotion_types = list(choices.keys())

    for emotion in emotion_types:
        question_type = random.randint(1, 2)

        if question_type == 1:
            questions.append(f"How does the clause '{clause}' from '{bill_name}' make you feel in terms of {emotion}?")
            for i, choice in enumerate(choices[emotion]):
                questions.append(f"{i+1}. {choice}")

        else:
            questions.append(f"Which of the following best describes your {emotion} response to the clause '{clause}' from '{bill_name}'?")
            for i, choice in enumerate(choices[emotion]):
                questions.append(f"{i+1}. {choice}")

    return questions

# Example Usage:
bill = "Bill C-21: Firearms Act"
clause_example = "Imposes stricter penalties for gun smuggling and illegal firearm trafficking."
emotion_choices = {
    "anger": [
        "Outraged at the leniency of current laws.",
        "Frustrated with the lack of effective enforcement.",
        "Indifferent to the penalties.",
        "Relieved that action is being taken.",
    ],
    "anxiety": [
        "Worried about increased surveillance.",
        "Anxious about potential misuse of power.",
        "Unconcerned about the changes.",
        "Hopeful that it will reduce gun violence.",
    ],
    "hope": [
        "Optimistic that it will reduce illegal gun activity.",
        "Slightly hopeful, but skeptical.",
        "No hope for change.",
        "Hopeful that it addresses root causes.",
    ],
    "fear": [
        "Fearful of increased police presence.",
        "Concerned about potential for racial profiling.",
        "Not fearful at all.",
        "Fearful that it won't be effective.",
    ],
    "optimism": [
      "Very optimistic about the changes.",
      "Moderately optimistic, with reservations.",
      "Not optimistic.",
      "Optimistic, but feel it's too little, too late."
    ]
}

generated_questions = generate_emotional_clause_questions_with_choices(bill, clause_example, emotion_choices)

print("Generated Questions:")
print("========================================")
for question in generated_questions:
    print(f"- {question}")
