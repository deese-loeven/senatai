import re

with open('app.py', 'r') as f:
    content = f.read()

# Find the profile route and simplify it
profile_route_pattern = r'''
@app\.route\(/profile\).*?def profile\(\):.*?return render_template\(.*?\)
'''

# Simple replacement - remove dividend calculation
content = re.sub(
    r"estimated_dividend = .*?\n",
    "",
    content
)

content = re.sub(
    r", dividend=estimated_dividend",
    "",
    content
)

with open('app.py', 'w') as f:
    f.write(content)

print("✅ Cleaned up profile route!")
