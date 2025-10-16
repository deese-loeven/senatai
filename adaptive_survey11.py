# adaptive_survey11_stable.py
import spacy
import psycopg2
import time 
import random
from collections import Counter

# --- Icebreaker List for Post and Ghost Feature ---
ICEBREAKERS = [
    "Vote booth open", "Democracy desk accepting visitors", "Your representative is listening (allegedly)", 
    "Polling station: open 24/7", "Ballot box ready for your thoughts", "Town hall in session", 
    "Public comment period: always open", "The floor is yours", "Your turn to speak", 
    "Democracy hotline: connected", "Let ’em know what you really think", "Say what you actually mean", 
    "No filter needed here", "Speak your mind", "Tell it like it is", "Get it off your chest", 
    "What’s really bothering you?", "Unload whatever’s on your mind", "No bullshit zone", 
    "Real talk time", "Complaints department is open", "Grievance office accepting submissions", 
    "Vent session: now live", "Complaint box: unlocked", "Problems? We’re listening", 
    "What’s broken today?", "Suggestion box (for angry suggestions)", "Customer feedback (government edition)", 
    "Comment card for democracy", "What needs fixing?", "What’s on your mind?", "Penny for your thoughts?", 
    "What matters to you?", "What keeps you up at night?", "What would you change?", 
    "If you could fix one thing…", "What’s your take?", "Got something to say?", 
    "What bugs you about this country?", "What should we be talking about?", "Rent too high? We’re listening", 
    "Frustration station: all aboard", "Mad as hell? Type it out", "Something pissing you off?", 
    "System broken? Tell us how", "Politicians not listening? We are", "Fed up? You’re not alone", 
    "What’s grinding your gears?", "Tired of being ignored? Not here", "Rage room (text edition)"
]

# --- Senatai Meta Check-in Questions ---
CHECK_IN_QUESTIONS = [
    {
        'text': "Do these questions feel clear and easy to answer?", 
        'options': ["1=Confusing", "2=A bit hard", "3=Neutral", "4=Clear", "5=Very Clear"],
        'type': 'clarity_check'
    },
    {
        'text': "How closely related are these questions to the issue you first typed?",
        'options': ["1=Not at all", "2=Slightly", "3=Moderately", "4=Closely", "5=Perfectly matched"],
        'type': 'relevance_check'
    },
    {
        'text': "Do you feel any of the questions are unfairly guiding your answer?",
        'options': ["1=Yes, definitely", "2=A little", "3=No", "4=Unsure", "5=I'm in control"],
        'type': 'bias_check'
    },
    {
        'text': "Are the concepts discussed too simple, too complex, or just right?",
        'options': ["1=Too Simple", "2=Simple", "3=Just Right", "4=Complex", "5=Too Complex"],
        'type': 'depth_check'
    },
    {
        'text': "Do you feel like you are answering too many questions?",
        'options': ["1=Yes, too many", "2=A few too many", "3=Just right", "4=I could do more", "5=I want more!"],
        'type': 'pacing_check'
    }
]


class AdaptiveSurveyV11:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.db_conn = psycopg2.connect(
            dbname="openparliament",
            user="dan", 
            password="senatai2025",
            host="localhost"
        )
        # Tracks total questions answered in the current session
        self.questions_answered_session = 0 
        
    def __del__(self):
        if self.db_conn:
            self.db_conn.close()

    # 🔑 FIX: Corrected variable unpacking and added ROLLBACK
    def get_bill_details(self, bill_number):
        """Get full bill details including text excerpts with defensive rollback."""
        cursor = None
        try:
            cursor = self.db_conn.cursor()
            
            # 1. Main bill fetch
            cursor.execute("""
                SELECT b.number, b.short_title_en, bt.summary_en, bt.text_en,
                       b.introduced, b.sponsor_politician_id
                FROM bills_bill b
                LEFT JOIN bills_billtext bt ON b.id = bt.bill_id
                WHERE b.number = %s
            """, (bill_number,))
            
            result = cursor.fetchone()
            
            if not result: 
                return None
            
            # CRITICAL FIX: Unpack in the same order as the SQL SELECT statement.
            number, short_title, summary, full_text, introduced_date, sponsor_id = result[:6] 

            # 2. Get sponsor name (Lookup in the correct 'politicians' table)
            sponsor = "Unknown"
            if sponsor_id:
                try:
                    # Assuming the table to find the politician's name is 'politicians_politician'
                    cursor.execute("SELECT name_en FROM politicians_politician WHERE id = %s", (sponsor_id,))
                    sponsor_result = cursor.fetchone()
                    sponsor = sponsor_result[0] if sponsor_result else "Unknown"
                except Exception:
                    # Ignore sponsor lookup failure, but keep the transaction clear
                    sponsor = "Unknown (Lookup Failed)"
            
            bill_url = f"https://openparliament.ca/bills/{number}/"
            excerpt = summary or (full_text[:170] + "...") if full_text else "No excerpt available."

            return {
                'number': number,
                'title': short_title or "Untitled Bill",
                'summary': summary,
                'excerpt': excerpt,
                'full_text': full_text,
                'introduced_date': introduced_date,
                'sponsor': sponsor,
                'url': bill_url
            }
        
        except Exception as e:
            # CRITICAL: If any database error occurs, we MUST rollback to clear the aborted transaction state
            self.db_conn.rollback()
            raise e # Re-raise the exception to the main thread for visibility
        
        finally:
            if cursor:
                cursor.close()

    # 🔑 FIX: Added defensive ROLLBACK
    def get_interest_count(self, bill_number):
        """Fetches the total count of distinct sessions this bill has been presented to *any* user."""
        cursor = None
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                SELECT COUNT(DISTINCT senatair_id, session_id) 
                FROM senatair_responses
                WHERE bill_number = %s;
            """, (bill_number,))
            count = cursor.fetchone()[0]
            return count
        except Exception:
            self.db_conn.rollback() # ADDED: Ensure rollback on failure
            return 0
        finally:
            if cursor:
                cursor.close()

    # 🔑 FIX: Added defensive ROLLBACK
    def find_relevant_bills(self, user_input):
        """Find bills relevant to user input using keyword matching"""
        doc = self.nlp(user_input.lower())
        keywords = []
        for token in doc:
            if (token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and 
                not token.is_stop and 
                len(token.text) > 3):
                keywords.append(token.lemma_.lower())
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'GPE', 'PERSON', 'LAW']:
                keywords.append(ent.text.lower())
        
        if not keywords: return [], []

        cursor = None
        try:
            cursor = self.db_conn.cursor()
            query = """
                SELECT DISTINCT bk.bill_number, COUNT(*) as match_count,
                               SUM(bk.relevance_score) as total_relevance
                FROM bill_keywords bk
                WHERE bk.keyword = ANY(%s)
                GROUP BY bk.bill_number
                ORDER BY total_relevance DESC, match_count DESC
                LIMIT 6
            """
            
            cursor.execute(query, (keywords,))
            results = cursor.fetchall()
            
            bills = []
            for bill_number, match_count, relevance in results:
                # This calls the fixed get_bill_details()
                bill_details = self.get_bill_details(bill_number) 
                if bill_details:
                    bill_details['match_count'] = match_count
                    bill_details['relevance'] = relevance
                    bills.append(bill_details)
            
            return bills, keywords
        
        except Exception as e:
            self.db_conn.rollback() # CRITICAL: Rollback if the main keyword search query fails
            # We don't re-raise here so the program can continue, but the main loop catches it anyway
            return [], []
        
        finally:
            if cursor:
                cursor.close()

    def display_bill_results(self, bills):
        """Clean display of relevant bills with proper links, including Senatai Interest Count."""
        print(f"\n📚 Found {len(bills)} relevant laws:")
        
        for i, bill in enumerate(bills, 1):
            interest_count = self.get_interest_count(bill['number'])
            interest_note = f" (🔥 Senatai Interest: {interest_count} Posts)" if interest_count > 0 else ""
            
            print(f"\n\t {i}. 📋 {bill['number']}: {bill['title']}{interest_note}")
            
            if 'sponsor' in bill: print(f"\t 👤 Sponsor: {bill['sponsor']}")
            if 'introduced_date' in bill: print(f"\t 📅 Introduced: {bill['introduced_date'] or 'Unknown date'}")
            if 'excerpt' in bill and bill['excerpt']: print(f"\t 📝 Excerpt: {bill['excerpt'][:170]}...")
            if 'url' in bill: print(f"\t 🔗 Full details: {bill['url']}")
            if 'relevance' in bill: print(f"\t 🎯 Relevance score: {bill['relevance']:.1f}")

    def generate_engaging_questions(self, bill):
        """Generate varied, engaging questions"""
        questions = []
        questions.append({
            'type': 'impact_assessment',
            'text': f"How significant do you believe the potential impact of {bill['number']} ({bill['title']}) will be?",
            'options': [
                "Extremely significant - could fundamentally change things", "Very significant - major implications", 
                "Moderately significant - noticeable effects", "Minimally significant - minor adjustments", "Unsure about potential impact"
            ]
        })
        questions.append({
            'type': 'tradeoff_question',
            'text': f"Considering {bill['number']}, where should the balance be struck between different interests?",
            'options': [
                "Strongly prioritize individual rights and freedoms", "Balance individual and collective interests equally", 
                "Lean toward collective benefits with safeguards", "Strongly prioritize collective/societal benefits", "Unsure about the right balance"
            ]
        })
        random.shuffle(questions)
        return questions[:2]
        
    def save_response(self, user_id, session_id, question, answer_score, bill_number, bill_keywords):
        """Saves a single user response to the senatair_responses table."""
        cursor = self.db_conn.cursor()
        
        try:
            is_meta = question.get('is_meta', False)
            
            cursor.execute("""
                INSERT INTO senatair_responses 
                (senatair_id, session_id, question_text, answer_text, bill_number, question_type, matched_keywords, is_meta, created_at) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (
                user_id,
                session_id,
                question['text'],
                question['options'][int(answer_score)-1],  # Store the text of the answer
                bill_number if not is_meta else None, 
                question['type'],
                ", ".join(bill_keywords) if bill_keywords else None,
                is_meta,
                time.strftime('%Y-%m-%d %H:%M:%S')
            ))
            self.db_conn.commit()
            return True
        except psycopg2.Error as e:
            self.db_conn.rollback() # Ensure rollback on failure
            return False
        finally:
            cursor.close()

    # --- NEW: Relevance Check Function ---
    def relevance_check_prompt(self, bills):
        """
        Asks the user to validate the list of bills or select one for a deep-dive.
        Returns a list of bills to generate questions about.
        """
        print("\n\n───────────────────────────────────────")
        print("🎯 RELEVANCE CHECK: Did we find the right laws?")
        print("───────────────────────────────────────")
        print("The system matched your input to the bills listed above. Please tell us:")
        
        bill_numbers = [bill['number'] for bill in bills]
        
        while True:
            # List options for clarity
            print(f"\nSelect a **Bill Number** (e.g., C-18) to focus on it, or choose one of the options below:")
            print(f"\t [A] - Generate questions for ALL {len(bills)} matched bills.")
            print(f"\t [B] - Skip the questions and return to the main prompt.")
            print(f"\t [quit] - Exit the application.")
            
            selection = input("Your choice (Bill Number/A/B/quit): ").strip().upper()
            
            if selection == 'QUIT':
                return None # Signal a program exit
            
            if selection == 'A':
                return bills # Proceed with all bills
            
            if selection == 'B':
                return [] # Skip questions
            
            if selection in bill_numbers:
                # Find the single bill object and return it in a list
                selected_bill = next((b for b in bills if b['number'] == selection), None)
                if selected_bill:
                    print(f"✅ Focusing questions only on {selected_bill['number']}: {selected_bill['title']}")
                    return [selected_bill]
                
            print("❌ Invalid input. Please enter a valid Bill Number (e.g., C-18), 'A', 'B', or 'quit'.")

    # --- NEW: Registration Prompt ---
    def registration_prompt(self, user_id, questions_answered):
        """Prompts the anonymous user to register after a threshold of answered questions."""
        if user_id == 1 and questions_answered >= 4:
            print("\n=======================================================")
            print("👋 Ready to make your voice count? (4 QUESTIONS ANSWERED)")
            print("=======================================================")
            print("You've contributed valuable input!")
            print("To turn your opinions into **Policap**—your share of political power and data revenue—you need to sign up for a free Senatai Co-op account.")
            print("\nWould you like to register or sign in now? (yes/no): ")
            
            response = input("> ").strip().lower()
            if response == 'yes':
                print("💻 Launching registration interface... (In a real app, this would open a web browser).")
                return True 
            else:
                print("👍 No problem. Continue posting anonymously. We'll remind you later.")
        return False

    # --- NEW: Senatai Check-in ---
    def senatai_check_in(self, user_id, session_id, current_q_count, keywords):
        """Checks in with the user every 7-10 questions."""
        # Check every 7 to 10 questions
        if current_q_count > 0 and current_q_count % random.randint(7, 10) == 0:
            print("\n\n═══════════════════════════════════════")
            print("🧠 SENATAI CHECK-IN: How's the AI doing?")
            print("───────────────────────────────────────")
            
            meta_q = random.choice(CHECK_IN_QUESTIONS)
            meta_q['is_meta'] = True
            
            print(f"❓ {meta_q['text']}\n")
            for j, option in enumerate(meta_q['options'], 1):
                print(f"    {j}. {option.split('=')[-1].strip()}")
            
            while True:
                response = input("\nYour choice (1-5 or 'skip' or 'quit'): ").strip().lower()
                
                if response == 'quit':
                    print("\n👋 Exiting survey...")
                    return True # Signal a program exit
                elif response == 'skip':
                    print("⏭️  Skipped check-in\n")
                    return False
                elif response in [str(i) for i in range(1, len(meta_q['options']) + 1)]:
                    self.save_response(
                        user_id=user_id,
                        session_id=session_id,
                        question=meta_q,
                        answer_score=response,
                        bill_number=None,
                        bill_keywords=keywords
                    )
                    print(f"✅ Check-in recorded: {meta_q['options'][int(response)-1].split('=')[-1].strip()}\n")
                    return False # Continue the survey
                else:
                    print("❌ Please enter 1-5, 'skip', or 'quit'")
        return False # Do not exit

    def run_survey(self):
        print("🚀 Starting Adaptive Survey V11")
        print("💡 Featuring Relevance Check, Senatai Check-in, Registration Prompt, and Graceful Exit!")
        
        # --- Test Environment Setup ---
        TEST_USER_ID = 1 # Using User ID 1 for testing (represents ANONYMOUS)
        TEST_SESSION_ID = int(time.time()) 
        print(f"👤 Using Test User ID: {TEST_USER_ID} | Session: {TEST_SESSION_ID}")
        print("---------------------------------")
        print("⏸️ Type 'quit' at any time to exit\n")
        
        # Reset session question counter
        self.questions_answered_session = 0
        
        while True:
            # Check for anonymous registration conversion
            if self.registration_prompt(TEST_USER_ID, self.questions_answered_session):
                break # Exit if user chooses to register

            current_icebreaker = random.choice(ICEBREAKERS)
            print("═══════════════════════════════════════")
            print(f"🗳️  {current_icebreaker}")
            print("───────────────────────────────────────")
            user_input = input("\n> ").strip()
            
            if user_input.lower() == 'quit':
                break
                
            if not user_input:
                continue
                
            print("🔍 Analyzing your concern...")
            
            try:
                # 1. Find bills and capture keywords (The 'Post' action)
                bills, keywords = self.find_relevant_bills(user_input) 
            except Exception as e:
                print(f"❌ An error occurred during bill search (Database might be down or locked): {e}")
                continue # Go back to the main loop

            
            if not bills:
                print("❌ No relevant legislation found. Try rephrasing your concern.")
                continue
            
            # Display bills with the new Senatai Interest Count
            self.display_bill_results(bills)
            
            # 2. NEW: Relevance Check Prompt
            bills_for_questions = self.relevance_check_prompt(bills)

            if bills_for_questions is None: # User typed 'quit' in the Relevance Check
                break
            if not bills_for_questions:
                continue # User chose to skip questions
            
            # 3. Generate all survey questions for the selected bills
            all_questions = []
            for bill in bills_for_questions:
                questions = self.generate_engaging_questions(bill)
                for q in questions:
                    q['bill'] = bill
                    all_questions.append(q)
            
            random.shuffle(all_questions)
            
            print(f"📝 Generated {len(all_questions)} questions based on your selection:\n")
            
            # 4. Start asking the survey questions
            for i, question in enumerate(all_questions[:8], 1):  # Limit to 8 questions
                
                # NEW: Senatai Check-in logic
                if self.senatai_check_in(TEST_USER_ID, TEST_SESSION_ID, self.questions_answered_session, keywords):
                    return # Exit if check-in returned 'quit'

                print(f"--- Question {i} ---")
                print(f"📋 Bill: {question['bill']['number']} - {question['bill']['title']}")
                print(f"❓ {question['text']}\n")
                
                for j, option in enumerate(question['options'], 1):
                    print(f"    {j}. {option}")
                
                while True:
                    # Graceful Exit FIX is inside this inner loop
                    response = input("\nYour choice (1-5 or 'skip' or 'quit'): ").strip().lower() 
                    
                    if response == 'quit':
                        print("\n👋 Exiting survey...")
                        return # Exit the run_survey method
                    
                    elif response == 'skip':
                        print("⏭️  Skipped question\n")
                        break
                        
                    elif response in ['1', '2', '3', '4', '5']:
                        print(f"✅ Response recorded: {question['options'][int(response)-1]}")
                        
                        # Save the content response
                        if self.save_response(
                            user_id=TEST_USER_ID,
                            session_id=TEST_SESSION_ID,
                            question=question,
                            answer_score=response, 
                            bill_number=question['bill']['number'],
                            bill_keywords=keywords 
                        ):
                            self.questions_answered_session += 1
                            print("💾 Answer successfully saved to database!\n")
                        else:
                            print("❌ Failed to save answer. The database may be locked. Continuing...\n")
                        break
                        
                    else:
                        print("❌ Please enter 1-5, 'skip', or 'quit'")
            
            print("🎉 Thank you for your input! Your responses help shape democratic engagement.")
            print("💡 Remember: You can view full bill details at the OpenParliament links above.\n")
            
if __name__ == "__main__":
    survey = AdaptiveSurveyV11()
    try:
        survey.run_survey()
    except Exception as e:
        print(f"\n🔥 FATAL ERROR: {e}")
