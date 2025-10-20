# Read the file
with open('policap_rewards.py', 'r') as f:
    content = f.read()

# Replace all ? placeholders with %s in SQL contexts
# This is safer than trying to match exact function blocks
lines = content.split('\n')
fixed_lines = []

for line in lines:
    if 'cursor.execute' in line and '?' in line:
        # Replace ? with %s in execute statements
        line = line.replace('?', '%s')
    fixed_lines.append(line)

content = '\n'.join(fixed_lines)

# Write back
with open('policap_rewards.py', 'w') as f:
    f.write(content)

print("✅ Fixed all ? placeholders in policap_rewards.py")
