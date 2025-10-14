# check_survey_storage.py
def check_survey_storage():
    with open('adaptive_survey3.py', 'r') as f:
        content = f.read()
    
    print("🔍 Analyzing adaptive_survey3.py response handling:")
    
    if 'answers' in content:
        print("   ✅ Has 'answers' variable")
        # Find where answers are processed
        lines = content.split('\n')
        answer_lines = [i for i, line in enumerate(lines) if 'answers' in line and '=' in line]
        for line_num in answer_lines[:3]:
            print(f"      Line {line_num}: {lines[line_num].strip()}")
    
    if 'save' in content and 'answer' in content:
        print("   ✅ Has answer saving logic")
    else:
        print("   ❌ No answer saving found")
    
    if 'database' in content and 'answer' in content:
        print("   ✅ Mentions database and answers")
    else:
        print("   ❌ No database answer storage")

if __name__ == "__main__":
    check_survey_storage()
