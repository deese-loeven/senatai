# adaptive_survey8.py
import spacy
import psycopg2
import time # Added for timestamp
import random
from collections import Counter

class AdaptiveSurveyV8:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.db_conn = psycopg2.connect(
            dbname="openparliament",
            user="dan", 
            password="senatai2025",
            host="localhost"
        )
        
    def get_bill_details(self, bill_number):
        """Get full bill details including text excerpts"""
        cursor = self.db_conn.cursor()
        
        # Use the correct table structure from your database
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
        
        # Get sponsor name if available
        sponsor = "Unknown"
        if sponsor_id:
            sponsor = self.get_sponsor_name(sponsor_id)
        
        # Extract a meaningful excerpt from the bill text
        excerpt = self.extract_meaningful_excerpt(full_text, summary)
        
        # Generate proper OpenParliament URL
        bill_url = f"https://openparliament.ca/bills/{number}/"
        
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
    
    def get_sponsor_name(self, sponsor_id):
        """Get sponsor name from politician ID"""
        try:
            cursor = self.db_conn.cursor()
            # Try to get name from bills_bill table first
            cursor.execute("SELECT name_en FROM bills_bill WHERE sponsor_politician_id = %s LIMIT 1", (sponsor_id,))
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else "Unknown"
        except:
            return "Unknown"
    
    def extract_meaningful_excerpt(self, full_text, summary):
        """Extract a meaningful clause or sentence from the bill text"""
        if not full_text:
            return summary or "No text available"
        
        # Try to find substantive clauses (avoid definitions and boilerplate)
        sentences = full_text.split('.')
        meaningful_sentences = []
        
        for sentence in sentences:
            clean_sentence = sentence.strip()
            if (len(clean_sentence) > 50 and 
                len(clean_sentence) < 300 and
                not clean_sentence.startswith(('Whereas', 'Therefore', 'Her Majesty', 'BE IT'))):
                # Look for substantive content
                if any(keyword in clean_sentence.lower() for keyword in 
                      ['shall', 'must', 'prohibit', 'require', 'establish', 'amend',
                       'provide', 'create', 'authorize', 'direct', 'enable']):
                    meaningful_sentences.append(clean_sentence)
        
        if meaningful_sentences:
            return meaningful_sentences[0] + "."
        elif summary:
            return summary
        else:
            # Fallback: first substantive sentence from full text
            for sentence in sentences:
                if len(sentence.strip()) > 30:
                    return sentence.strip() + "."
            return full_text[:200] + "..."
    
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
        
        print(f"🎯 Your concerns: {keywords[:10]}")
        
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
        
        return bills
    
    def generate_engaging_questions(self, bill):
        """Generate varied, engaging questions using actual bill content"""
        questions = []
        
        # Question type 1: Direct clause question
        if bill['excerpt'] and len(bill['excerpt']) > 30:
            questions.append({
                'type': 'clause_opinion',
                'text': f"Consider this provision from {bill['number']}:\n\n\"{bill['excerpt']}\"\n\nHow do you feel about this approach?",
                'options': [
                    "Strongly support this direction",
                    "Support with minor concerns", 
                    "Neutral or unsure",
                    "Oppose with reservations",
                    "Strongly oppose this approach"
                ]
            })
        
        # Question type 2: Impact assessment
        questions.append({
            'type': 'impact_assessment',
            'text': f"How significant do you believe the potential impact of {bill['number']} ({bill['title']}) will be?",
            'options': [
                "Extremely significant - could fundamentally change things",
                "Very significant - major implications",
                "Moderately significant - noticeable effects",
                "Minimally significant - minor adjustments",
                "Unsure about potential impact"
            ]
        })
        
        # Question type 3: Priority ranking
        if bill['summary']:
            questions.append({
                'type': 'priority_ranking', 
                'text': f"Given that {bill['number']} addresses {bill['summary'][:100]}..., how high of a priority should this be for Parliament?",
                'options': [
                    "Critical priority - address immediately",
                    "High priority - important to resolve soon",
                    "Medium priority - should be addressed",
                    "Low priority - can wait for other issues",
                    "Not a priority - focus elsewhere"
                ]
            })
        
        # Question type 4: Trade-off question
        questions.append({
            'type': 'tradeoff_question',
            'text': f"Considering {bill['number']}, where should the balance be struck between different interests?",
            'options': [
                "Strongly prioritize individual rights and freedoms",
                "Balance individual and collective interests equally",
                "Lean toward collective benefits with safeguards",
                "Strongly prioritize collective/societal benefits",
                "Unsure about the right balance"
            ]
        })
        
        # Shuffle and return top 2 questions per bill
        random.shuffle(questions)
        return questions[:2]
    
    def display_bill_results(self, bills):
        """Clean display of relevant bills with proper links"""
        print(f"\n📚 Found {len(bills)} relevant laws:\n")
        
        for i, bill in enumerate(bills, 1):
            print(f"   {i}. 📋 {bill['number']}: {bill['title']}")
            print(f"      👤 Sponsor: {bill['sponsor']}")
            print(f"      📅 Introduced: {bill['introduced_date'] or 'Unknown date'}")
            if bill['summary']:
                print(f"      📝 Summary: {bill['summary'][:150]}...")
            print(f"      🔗 Full details: {bill['url']}")
            print(f"      🎯 Relevance score: {bill['relevance']:.1f}")
            print()
    
    def run_survey(self):
        print("🚀 Starting Adaptive Survey V8")
        print("💡 Now with actual bill excerpts & proper links!")
        print("⏸️  Type 'quit' at any time to exit\n")
        
        while True:
            user_input = input("\n🗳️  What's on your mind? We'll match it to actual legislation...\n\n> ").strip()
            
            if user_input.lower() == 'quit':
                break
                
            if not user_input:
                continue
            
            print("🔍 Analyzing your concern...")
            bills = self.find_relevant_bills(user_input)
            
            if not bills:
                print("❌ No relevant legislation found. Try rephrasing your concern.")
                continue
            
            self.display_bill_results(bills)
            
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
            
            for i, question in enumerate(all_questions[:8], 1):  # Limit to 8 questions
                print(f"--- Question {i} ---")
                print(f"📋 Bill: {question['bill']['number']} - {question['bill']['title']}")
                print(f"❓ {question['text']}\n")
                
                for j, option in enumerate(question['options'], 1):
                    print(f"   {j}. {option}")
                
                while True:
                    response = input("\nYour choice (1-5 or 'skip'): ").strip().lower()
                    if response == 'skip':
                        print("⏭️  Skipped question\n")
                        break
                    elif response in ['1', '2', '3', '4', '5']:
                        print(f"✅ Response recorded: {question['options'][int(response)-1]}\n")
                        break
                    else:
                        print("❌ Please enter 1-5 or 'skip'")
            
            print("🎉 Thank you for your input! Your responses help shape democratic engagement.")
            print("💡 Remember: You can view full bill details at the OpenParliament links above.\n")
    def save_response(self, user_id, session_id, question, answer_score, bill_number, bill_keywords):
        """Saves a single user response to the senatair_responses table."""
        cursor = self.db_conn.cursor()
        
        # NOTE: answer_score is saved as TEXT, but it holds the numeric value (1-5)
        # We will use this numeric value for prediction.
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
                ", ".join(bill_keywords), # Storing the keywords that matched the bill
                time.strftime('%Y-%m-%d %H:%M:%S')
            ))
            self.db_conn.commit()
            return True
        except psycopg2.Error as e:
            print(f"Database error saving response: {e}")
            self.db_conn.rollback()
            return False
        finally:
            cursor.close()

    def run_survey(self):
        print("🚀 Starting Adaptive Survey V8")
        print("💡 Now with actual bill excerpts & proper links!")
        print("--- Test Environment Settings ---")
        TEST_USER_ID = 1 # Replace with actual auth user ID
        TEST_SESSION_ID = int(time.time()) # Simple unique session ID
        print(f"👤 Using Test User ID: {TEST_USER_ID} | Session: {TEST_SESSION_ID}")
        print("---------------------------------")
        print("⏸️ Type 'quit' at any time to exit\n")
        
        # ... (Previous run_survey logic) ...
        
        while True:
            # ... (User input logic) ...
            
            print("🔍 Analyzing your concern...")
            
            # --- Capture Keywords used for Bill Matching (CRITICAL for Predictor) ---
            doc = self.nlp(user_input.lower())
            keywords = []
            for token in doc:
                if (token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and not token.is_stop and len(token.text) > 3):
                    keywords.append(token.lemma_.lower())
            
            # --- Find Relevant Bills ---
            # NOTE: find_relevant_bills currently calls cursor.execute(query, (keywords,))
            # We assume 'bills' now contains the bill details matched by 'keywords'
            bills = self.find_relevant_bills(user_input) 
            
            # ... (Display bills logic) ...
            
            # ... (Generate questions logic) ...
            
            for i, question in enumerate(all_questions[:8], 1):
                # ... (Display question and options) ...
                
                while True:
                    response = input("\nYour choice (1-5 or 'skip'): ").strip().lower()
                    
                    if response == 'skip':
                        print("⏭️ Skipped question\n")
                        break
                    elif response in ['1', '2', '3', '4', '5']:
                        print(f"✅ Response recorded: {question['options'][int(response)-1]}")
                        
                        # --- 🔑 SAVE TO DATABASE HERE ---
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
            
            # ... (Thank you message) ...
if __name__ == "__main__":
    survey = AdaptiveSurveyV8()
    survey.run_survey()
