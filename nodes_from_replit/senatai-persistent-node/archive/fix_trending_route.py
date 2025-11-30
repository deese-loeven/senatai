import re

with open('app.py', 'r') as f:
    content = f.read()

# Fix the trending route - change 'topic_name' to the correct column name
content = re.sub(
    r"total_complaints = cursor\.fetchone\(\)\['topic_name'\]",
    "total_complaints = cursor.fetchone()[0]",
    content
)

with open('app.py', 'w') as f:
    f.write(content)

print("✅ Fixed trending route column reference")
