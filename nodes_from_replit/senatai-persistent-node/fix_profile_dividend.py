# Read the profile template
with open('templates/profile.html', 'r') as f:
    content = f.read()

# Remove the dividend line that's causing the error
content = content.replace('<div class="dividend-amount">${{ "%.2f"|format(dividend) }}</div>', '')

with open('templates/profile.html', 'w') as f:
    f.write(content)

print("✅ Removed dividend reference from profile template")
