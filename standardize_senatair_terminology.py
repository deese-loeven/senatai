import os
import re

def update_senatair_terminology(filename):
    """Replace user/users with Senatair/Senatairs where appropriate"""
    try:
        with open(filename, 'r') as file:
            content = file.read()
        
        # Replace user -> Senatair (when referring to people, not in code contexts)
        # Be careful not to replace in variable names, function names, or SQL keywords
        content = re.sub(r'\buser\b', 'Senatair', content)
        content = re.sub(r'\busers\b', 'Senatairs', content)
        
        # Update database table names carefully
        content = re.sub(r'CREATE TABLE users\b', 'CREATE TABLE Senatairs', content)
        content = re.sub(r'CREATE TABLE IF NOT EXISTS users\b', 'CREATE TABLE IF NOT EXISTS Senatairs', content)
        content = re.sub(r'\busers\b', 'Senatairs', content)  # General replacement
        
        # Update column references
        content = re.sub(r'\buser_id\b', 'Senatair_id', content)
        content = re.sub(r'\buser_name\b', 'Senatair_name', content)
        
        with open(filename, 'w') as file:
            file.write(content)
        print(f"✓ Updated: {filename}")
        return True
    except Exception as e:
        print(f"✗ Error updating {filename}: {e}")
        return False

# Files to update (focus on application logic files, not NLP files)
files_to_update = [
    'survey_app2.py', 'survey_app3.py', 'survey_app4.py', 'survey_app5.py', 'survey_app6.py',
    'survey_appdeepseek1.py', 'survey_appdeepseek2.py', 'survey_appdeepseek3.py',
    'survey_appgemini1.py', 'survey_appgemini2.py', 'survey_appgemini3.py',
    'survey_app.py', 'survey_database.py', 'database.py', 'database_deepseek2.py',
    'vote_auditor1.py', 'vote_auditor2.py', 'vote_auditor_deepseek1.py', 'vote_auditorgemini1.py',
    'vote_predictor.py', 'vote_predictor3.py', 'dashboard1.py', 'authentication_module1.py'
]

print("Starting Senatair terminology standardization...")
updated_count = 0

for file in files_to_update:
    if os.path.exists(file):
        if update_senatair_terminology(file):
            updated_count += 1

print(f"\nSenatair standardization complete! Updated {updated_count} files.")
