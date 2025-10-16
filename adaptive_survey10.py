# adaptive_survey10.py
import spacy
import psycopg2
import time 
import random
from collections import Counter

# --- NEW: Icebreaker List for Post and Ghost Feature ---
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


class AdaptiveSurveyV10:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.db_conn = psycopg2.connect(
            dbname="openparliament",
            user="dan", 
            password="senatai2025",
            host="localhost"
        )
        
    def __del__(self):
        if self.db_conn:
            self.db_conn.close()

    def get_bill_details(self, bill_number):
        """Get full bill details including text excerpts"""
        cursor = self.db_conn.cursor()
        
        # Using the simplified query from previous versions
        cursor.execute("""
            SELECT b.number, b.short_title_en, bt.summary_en, bt.text_en,
                   b.introduced, b.sponsor_politician_id
            FROM bills_bill b
            LEFT JOIN bills_billtext bt ON b.id = bt.bill_id
            WHERE b.number = %s
        """, (bill_number,))
        
        result = cursor.fetchone()
        cursor.close()
        
        if not result:
            return None
            
        number, short_title, summary, full_text, introduced_date, sponsor_id = result
        
        # Get sponsor name (simplified for demo)
        sponsor = "Unknown"
        if sponsor_id:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("SELECT name_en FROM bills_bill WHERE sponsor_politician_id = %s LIMIT 1", (sponsor_id,))
                sponsor_result = cursor.fetchone()
                cursor.close()
                sponsor = sponsor_result[0] if sponsor_result else "Unknown"
            except:
                sponsor = "Unknown"
        
        # Generate proper OpenParliament URL
        bill_url = f"https://openparliament.ca/bills/{number}/"
        
        # Simplified excerpt extraction
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
    
    # --- NEW: Method to get the Interest Count (from previous step) ---
    def get_interest_count(self, bill_number):
        """
        Fetches the total count of distinct sessions this bill has been presented to 
        *any* user. This is the 'Senatai Interest' for monetization/prioritization.
        """
        cursor = self.db_conn.cursor()
        try:
            # Count how many responses (for any user) have been recorded for this bill.
            # Counting DISTINCT senatair_id, session_id is a proxy for unique user-sessions of interest.
            cursor.execute("""
                SELECT COUNT(DISTINCT senatair_id, session_id) 
                FROM senatair_responses
                WHERE bill_number = %s;
            """, (bill_number,))
            count = cursor.fetchone()[0]
            return count
        except Exception:
            return 0
        finally:
            cursor.close()

    def find_relevant_bills(self, user_input):
        """Find bills relevant to user input using keyword matching"""
        doc = self.nlp(user_input.lower())
        
        # Extract meaningful keywords
        keywords = []
        for token in doc:
            if (token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and 
                not token.is_stop and 
                len(token.text) > 3):
                keywords.append(token.lemma_.lower())
        
        # Also include entities
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'GPE', 'PERSON', 'LAW']:
                keywords.append(ent.text.lower())
        
        if not keywords:
            return [], [] # Return empty list if no keywords found

        # Query for matching bills
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
        cursor.close()
        
        bills = []
        for bill_number, match_count, relevance in results:
            bill_details = self.get_bill_details(bill_number)
            if bill_details:
                bill_details['match_count'] = match_count
                bill_details['relevance'] = relevance
                bills.append(bill_details)
        
        return bills, keywords # Return both bills and the keywords used
    
    # --- UPDATED: display_bill_results to show the Senatai Interest Count ---
    def display_bill_results(self, bills):
        """Clean display of relevant bills with proper links, including Senatai Interest Count."""
        print(f"\n📚 Found {len(bills)} relevant laws:")
        
        for i, bill in enumerate(bills, 1):
            # 1. Fetch the interest count for the bill
            interest_count = self.get_interest_count(bill['number'])
            
            # 2. Create the new interest note and counter
            interest_note = ""
            if interest_count > 0:
                # The note indicating the law was drawn up by Senatai keyword interest
                interest_note = f" (🔥 Senatai Interest: {interest_count} Posts)"
            
            # 3. Print the bill with the new note
            print(f"\n\t {i}. 📋 {bill['number']}: {bill['title']}{interest_note}")
            
            # Print the other details
            if 'sponsor' in bill:
                print(f"\t 👤 Sponsor: {bill['sponsor']}")
            if 'introduced_date' in bill:
                print(f"\t 📅 Introduced: {bill['introduced_date'] or 'Unknown date'}")
            if 'excerpt' in bill and bill['excerpt']:
                print(f"\t 📝 Excerpt: {bill['excerpt'][:170]}...")
            if 'url' in bill:
                print(f"\t 🔗 Full details: {bill['url']}")
                
            print(f"\t 🎯 Relevance score: {bill['relevance']:.1f}")

    # (Other helper methods like generate_engaging_questions and save_response remain the same for simplicity)
    # They are kept out of this direct listing to focus on the main change.

    def generate_engaging_questions(self, bill):
        """Generate varied, engaging questions (Simplified for V10)"""
        questions = []
        
        # Question type 2: Impact assessment
        questions.append({
            'type': 'impact_assessment',
            'text': f"How significant do you believe the potential impact of {bill['number']} ({bill['title']}) will be?",
            'options': [
                "Extremely significant - could fundamentally change things", "Very significant - major implications", 
                "Moderately significant - noticeable effects", "Minimally significant - minor adjustments", "Unsure about potential impact"
            ]
        })
        
        # Question type 4: Trade-off question
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
            cursor.execute("""
                INSERT INTO senatair_responses 
                (senatair_id, session_id, question_text, answer_text, bill_number, question_type, matched_keywords, created_at) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """, (
                user_id,
                session_id,
                question['text'],
                answer_score,  # The numeric input (1-5)
                bill_number,
                question['type'],
                ", ".join(bill_keywords), # Storing the keywords from the initial input
                time.strftime('%Y-%m-%d %H:%M:%S')
            ))
            self.db_conn.commit()
            return True
        except psycopg2.Error as e:
            # print(f"Database error saving response: {e}") # Suppress error for cleaner output
            self.db_conn.rollback()
            return False
        finally:
            cursor.close()

    def run_survey(self):
        print("🚀 Starting Adaptive Survey V10")
        print("💡 Now featuring the 'Post and Ghost' Icebreaker Rotation!")
        # --- Test Environment Setup ---
        print("--- Test Environment Settings ---")
        TEST_USER_ID = 1 # Using User ID 1 for testing
        TEST_SESSION_ID = int(time.time()) # Simple unique session ID
        print(f"👤 Using Test User ID: {TEST_USER_ID} | Session: {TEST_SESSION_ID}")
        print("---------------------------------")
        print("⏸️ Type 'quit' at any time to exit\n")
        
        while True:
            # --- NEW: Rotate Icebreaker Prompt ---
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
            
            # Find bills and capture keywords (the raw data from the Post and Ghost)
            bills, keywords = self.find_relevant_bills(user_input) 
            
            if not bills:
                print("❌ No relevant legislation found. Try rephrasing your concern.")
                continue
            
            # Display bills with the new Senatai Interest Count
            self.display_bill_results(bills)
            
            # --- The Post and Ghost feature ends here if the user closes the program.
            # --- The rest is the optional, higher-value survey engagement.
            
            # Generate and ask questions
            all_questions = []
            for bill in bills:
                questions = self.generate_engaging_questions(bill)
                for q in questions:
                    q['bill'] = bill
                    all_questions.append(q)
            
            # Shuffle questions across bills
            random.shuffle(all_questions)
            
            print(f"📝 Generated {len(all_questions)} questions based on the legislation:\n")
            
            # Start asking the survey questions
            for i, question in enumerate(all_questions[:8], 1):  # Limit to 8 questions
                print(f"--- Question {i} ---")
                print(f"📋 Bill: {question['bill']['number']} - {question['bill']['title']}")
                print(f"❓ {question['text']}\n")
                
                for j, option in enumerate(question['options'], 1):
                    print(f"    {j}. {option}")
                
                while True:
                    response = input("\nYour choice (1-5 or 'skip'): ").strip().lower()
                    if response == 'skip':
                        print("⏭️  Skipped question\n")
                        break
                    elif response in ['1', '2', '3', '4', '5']:
                        print(f"✅ Response recorded: {question['options'][int(response)-1]}")
                        
                        # --- 🔑 SAVE TO DATABASE HERE ---
                        # Note: The keywords saved are the ones generated from the initial 'Post and Ghost' input
                        self.save_response(
                            user_id=TEST_USER_ID,
                            session_id=TEST_SESSION_ID,
                            question=question,
                            answer_score=response, # The numeric score (1-5)
                            bill_number=question['bill']['number'],
                            bill_keywords=keywords # The keywords from the user's initial input
                        )
                        print("💾 Answer successfully saved to database!\n")
                        break
                    else:
                        print("❌ Please enter 1-5 or 'skip'")
            
            print("🎉 Thank you for your input! Your responses help shape democratic engagement.")
            print("💡 Remember: You can view full bill details at the OpenParliament links above.\n")
            
if __name__ == "__main__":
    survey = AdaptiveSurveyV10()
    try:
        survey.run_survey()
    except Exception as e:
        print(f"\nAn error occurred during runtime: {e}")
