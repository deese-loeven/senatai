import re

with open('app.py', 'r') as f:
    content = f.read()

# Remove the dividend calculation and display from profile route
content = re.sub(
    r"estimated_dividend = balance \* 0\.50.*?return render_template\('profile\.html',.*?dividend=estimated_dividend,",
    "return render_template('profile.html', balance=balance, transactions=transactions, total_votes=total_votes)",
    content,
    flags=re.DOTALL
)

# Alternative: Just remove the dividend from the template data
content = re.sub(
    r", dividend=estimated_dividend",
    "",
    content
)

with open('app.py', 'w') as f:
    f.write(content)

print("✅ Removed dividend display from profile!")
