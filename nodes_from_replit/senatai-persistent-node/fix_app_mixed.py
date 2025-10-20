with open('app.py', 'r') as f:
    content = f.read()

# Fix the specific mixed syntax lines
content = content.replace(
    "cursor.execute('UPDATE topic_interest SET interest_count = interest_count + 1, last_mentioned = ? WHERE topic_name = %s',",
    "cursor.execute('UPDATE topic_interest SET interest_count = interest_count + 1, last_mentioned = %s WHERE topic_name = %s',"
)

content = content.replace(
    "SET bill_title = ?, bill_summary = ?, full_text = ?, status = ?, category = ?, source_url = ?",
    "SET bill_title = %s, bill_summary = %s, full_text = %s, status = %s, category = %s, source_url = %s"
)

with open('app.py', 'w') as f:
    f.write(content)

print("✅ Fixed mixed syntax in app.py")
