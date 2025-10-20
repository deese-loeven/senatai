import re

with open('app.py', 'r') as f:
    content = f.read()

# Update the home route to count from legislation table
content = re.sub(
    r"cursor\.execute\('SELECT COUNT\(\*\) FROM legislation'\)",
    "cursor.execute('SELECT COUNT(*) FROM legislation')",
    content
)

with open('app.py', 'w') as f:
    f.write(content)

print("✅ Fixed bill count query!")
