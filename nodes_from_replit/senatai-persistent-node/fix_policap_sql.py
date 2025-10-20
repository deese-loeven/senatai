import re

# Read the policap_rewards.py file
with open('policap_rewards.py', 'r') as f:
    content = f.read()

# Replace SQLite ? placeholders with PostgreSQL %s placeholders
content = re.sub(r"user_id = \?", "user_id = %s", content)
content = re.sub(r"activity_date = \?", "activity_date = %s", content)
content = re.sub(r"user_id=\?", "user_id=%s", content)

# Also fix any other potential ? placeholders in SQL queries
content = re.sub(r"WHERE.*?\?", lambda match: match.group(0).replace('?', '%s'), content)

with open('policap_rewards.py', 'w') as f:
    f.write(content)

print("✅ Fixed SQL syntax in policap_rewards.py")
