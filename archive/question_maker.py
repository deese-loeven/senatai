import random

def generate_legislation_question(legislation_data):
    """
    Generates a yes/no question based on a piece of legislation.

    Args:
        legislation_data (list): A list of dictionaries, where each dictionary
                                 represents a piece of legislation.

    Returns:
        str: A generated yes/no question.
    """

    if not legislation_data:
        return "No legislation data available."

    legislation = random.choice(legislation_data)  # Select a random legislation

    bill_title = legislation.get("title", "this bill")  # Get bill title or default
    bill_description = legislation.get("description", "the proposed changes") #get bill description or default.

    question_templates = [
        f"Does the bill titled '{bill_title}' propose {bill_description}?",
        f"Is it true that '{bill_title}' will impact {bill_description}?",
        f"Will '{bill_title}' result in {bill_description}?",
        f"Are the changes proposed in '{bill_title}' {bill_description}?"
    ]

    return random.choice(question_templates)

# Example Usage (Assuming 'legislation_data' is your loaded data):
legislation_data = [
    {
        "title": "Bill 123: Affordable Housing Act",
        "description": "increased funding for social housing",
    },
    {
        "title": "Bill 456: Environmental Protection Bill",
        "description": "new regulations on industrial emissions",
    },
    {
        "title": "Bill 789: Education Modernization Act",
        "description": "the implementation of online learning platforms",
    }
]

question = generate_legislation_question(legislation_data)
print(question)
