# test_adaptive_survey9.py
import adaptive_survey9
import time
import sys

# Instantiate the main class
try:
    survey = adaptive_survey9.AdaptiveSurveyV8()
except Exception as e:
    print(f"❌ TEST FAILED: Could not instantiate AdaptiveSurveyV8. Check DB connection.")
    print(f"Error: {e}")
    sys.exit(1)

print("✅ TEST PASSED: AdaptiveSurveyV8 instantiated and DB connection successful.")

# --- Test 1: Bill Detail Fetching ---
print("\n--- Running Test 1: Bill Detail Fetching ---")
# Use a known bill number that is likely to exist
TEST_BILL_NUMBER = 'C-45' 
bill_details = survey.get_bill_details(TEST_BILL_NUMBER)

if bill_details and bill_details.get('number') == TEST_BILL_NUMBER:
    print(f"✅ TEST PASSED: Fetched details for {TEST_BILL_NUMBER} ({bill_details['title']}).")
    print(f"   Excerpt length: {len(bill_details['excerpt'])} characters.")
else:
    print(f"❌ TEST FAILED: Could not fetch bill details for {TEST_BILL_NUMBER}. (Check bills_bill and bills_billtext tables)")
    sys.exit(1)

# --- Test 2: Keyword Matching ---
print("\n--- Running Test 2: Keyword Matching ---")
TEST_INPUT = "I am concerned about the rising cost of housing and lack of affordable childcare."
relevant_bills = survey.find_relevant_bills(TEST_INPUT)

if relevant_bills:
    print(f"✅ TEST PASSED: Found {len(relevant_bills)} relevant bills for user input.")
    print(f"   Top match: {relevant_bills[0]['number']} ({relevant_bills[0]['relevance']:.2f} score)")
else:
    print("❌ TEST FAILED: Found 0 relevant bills. (Check spacy load and bill_keywords table)")
    sys.exit(1)

# --- Test 3: Save Response Simulation ---
print("\n--- Running Test 3: Save Response Simulation ---")
mock_question = {
    'text': 'How do you feel about this test provision?',
    'type': 'test_type'
}
mock_keywords = ['test_keyword', 'simulation']
mock_bill = 'S-999'

# Simulate saving a response (1=Strongly support)
save_success = survey.save_response(
    user_id=999,
    session_id=int(time.time()),
    question=mock_question,
    answer_score='1',
    bill_number=mock_bill,
    bill_keywords=mock_keywords
)

if save_success:
    print("✅ TEST PASSED: Simulated response successfully saved to database.")
else:
    print("❌ TEST FAILED: Database save operation failed.")
    sys.exit(1)

print("\n🎉 All core tests passed. adaptive_survey9.py looks solid!")
survey.__del__() # Close DB connection
