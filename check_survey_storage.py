# check_survey_storage.py
def check_survey_storage():
    # 🎯 TARGETING THE LATEST FILE AFTER REFACTORING
    TARGET_FILE = 'adaptive_survey11.py'
    
    try:
        with open(TARGET_FILE, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ ERROR: File not found. You must update this script to target a file that exists, like {TARGET_FILE}.")
        return

    print(f"🔍 Analyzing {TARGET_FILE} response handling:")
    
    # Check for core components
    if 'save_response' in content:
        print("    ✅ Has 'save_response' function")
        
    if 'questions_answered_session' in content:
        print("    ✅ Tracks 'questions_answered_session'")
        
    if 'db_conn.commit()' in content and 'db_conn.rollback()' in content:
        print("    ✅ Database transaction handling is present (COMMIT/ROLLBACK)")
    else:
        print("    ⚠️ Missing safe database transaction handling (COMMIT/ROLLBACK)")
    
    # Check if bill number is saved
    if 'bill_number=question' in content:
        print("    ✅ Saving bill_number in question data")

if __name__ == "__main__":
    check_survey_storage()
