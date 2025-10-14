# check_existing_auth.py
import os

def analyze_auth_files():
    auth_files = [
        'authentication_module1.py',
        'survey_app6_final_working.py', 
        'survey_app_improved.py',
        'survey_database.py'
    ]
    
    for file in auth_files:
        if os.path.exists(file):
            print(f"\n🔍 Analyzing {file}:")
            try:
                with open(file, 'r') as f:
                    content = f.read()
                    
                if 'user' in content.lower() or 'login' in content.lower():
                    print(f"   ✅ Contains user/auth code")
                    # Show relevant lines
                    lines = content.split('\n')
                    user_lines = [line for line in lines if 'user' in line.lower() or 'login' in line.lower() or 'password' in line.lower()]
                    for line in user_lines[:5]:  # Show first 5 relevant lines
                        print(f"      {line.strip()}")
                else:
                    print(f"   ❌ No user/auth code found")
                    
            except Exception as e:
                print(f"   ❌ Error reading: {e}")

if __name__ == "__main__":
    analyze_auth_files()
