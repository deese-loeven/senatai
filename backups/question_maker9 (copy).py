#!/usr/bin/env python3
import random
import sys
from functools import wraps
import time

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

THEMES = {
    "economic": ["taxation", "economic growth", "small businesses"],
    "social": ["healthcare", "education", "child care"],
    "rights": ["free speech", "privacy", "gun rights"]
}

@timeout()
def generate_question():
    theme = random.choice(random.choice(list(THEMES.values())))
    return f"How important is {theme} to you? (Scale 1-5)"

if __name__ == "__main__":
    try:
        print(generate_question())
    except TimeoutError:
        print("Question generation timed out", file=sys.stderr)
        sys.exit(1)
