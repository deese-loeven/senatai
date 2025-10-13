import re

# Read the file
with open('survey_app6.py', 'r') as file:
    content = file.read()

# Replace all token references with policaps
content = re.sub(r'\btokens\b', 'policaps', content)

# Replace users table references with Users (since your schema uses "Users" with capital U)
content = re.sub(r'\busers\b', 'Users', content)

# Replace id column with user_id (since your schema uses user_id, not id)
content = re.sub(r'WHERE id =', 'WHERE user_id =', content)
content = re.sub(r'\(id,\)', '(user_id,)', content)

# Write back
with open('survey_app6.py', 'w') as file:
    file.write(content)

print("✓ Comprehensive fixes applied to survey_app6.py")
print("Changes made:")
print("  - tokens → policaps")
print("  - users → Users") 
print("  - id → user_id")
