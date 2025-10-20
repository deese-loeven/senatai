import re

with open('app.py', 'r') as f:
    content = f.read()

# 1. Fix the user_loader to use senatairs table
content = re.sub(
    r"cursor\.execute\('SELECT id, username, policap_balance, CAST\(is_admin AS INTEGER\) as is_admin FROM users WHERE id = %s', \(user_id,\)\)",
    "cursor.execute('SELECT id, username, policaps as policap_balance, CAST(is_admin AS INTEGER) as is_admin FROM senatairs WHERE id = %s', (user_id,))",
    content
)

# 2. Fix profile route policap_transactions query
content = re.sub(
    r"cursor\.execute\('SELECT \* FROM policap_transactions WHERE user_id = %s ORDER BY timestamp DESC LIMIT 10',",
    "cursor.execute('SELECT * FROM policap_transactions WHERE senatair_id = %s ORDER BY timestamp DESC LIMIT 10',",
    content
)

# 3. Fix signup route to insert into senatairs
content = re.sub(
    r"cursor\.execute\('INSERT INTO users \(username, password_hash\) VALUES \(%s, %s\)', \(username, password_hash\)\)",
    "cursor.execute('INSERT INTO senatairs (username, password_hash) VALUES (%s, %s)', (username, password_hash))",
    content
)

# 4. Fix login route to query senatairs
content = re.sub(
    r"cursor\.execute\('SELECT id, username, password_hash, policap_balance, is_admin, accepted_terms, accepted_coop_agreement FROM users WHERE username = %s', \(username,\)\)",
    "cursor.execute('SELECT id, username, password_hash, policaps as policap_balance, is_admin, accepted_terms, accepted_coop_agreement FROM senatairs WHERE username = %s', (username,))",
    content
)

# 5. Fix agreements route to update senatairs
content = re.sub(
    r"cursor\.execute\('UPDATE users SET accepted_terms = TRUE, accepted_coop_agreement = TRUE WHERE id = %s',",
    "cursor.execute('UPDATE senatairs SET accepted_terms = TRUE, accepted_coop_agreement = TRUE WHERE id = %s',",
    content
)

# 6. Fix vote route user queries
content = re.sub(
    r"cursor\.execute\('SELECT policap_balance FROM users WHERE id = %s', \(current_user\.id,\)\)",
    "cursor.execute('SELECT policaps as policap_balance FROM senatairs WHERE id = %s', (current_user.id,))",
    content
)

content = re.sub(
    r"cursor\.execute\('UPDATE users SET policap_balance = policap_balance \+ %s WHERE id = %s',",
    "cursor.execute('UPDATE senatairs SET policaps = policaps + %s WHERE id = %s',",
    content
)

with open('app.py', 'w') as f:
    f.write(content)

print("✅ Comprehensive fixes applied!")
