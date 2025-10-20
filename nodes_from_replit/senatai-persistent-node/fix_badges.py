with open('badges.py', 'r') as f:
    content = f.read()

# Replace ? with %s
content = content.replace('?', '%s')

with open('badges.py', 'w') as f:
    f.write(content)

print("✅ Fixed badges.py")
