# adaptive_survey_v4_complete.py
from senatair_auth import SenatairAuth
import psycopg2
import random
import re
from collections import Counter

class AdaptiveSurveyV4:
    def __init__(self):
        self.auth = SenatairAuth()
        self.conn = psycopg2.connect(
            dbname="openparliament",
            user="dan",
            password="senatai2025", 
            host="localhost"
        )
        self.current_senatair = None
        self.current_session = None
        self.session_count = 0
    
    def login_or_register(self):
        """Handle Senatair login or registration"""
        print("\n🔐 SENATAIR AUTHENTICATION")
        print("1. Login")
        print("2. Register") 
        print("3. Continue as Guest")
        
        choice = input("\nChoose option (1-3): ").strip()
        
        if choice == "1":
            username = input("Username: ").strip()
            senatair = self.auth.get_senatair(username)
            if senatair:
                self.current_senatair = senatair
                print(f"✅ Welcome back, {senatair['username']}!")
                print(f"💰 You have {senatair['policaps']} Policaps")
                return True
            else:
                print("❌ User not found")
                return False
                
        elif choice == "2":
            username = input("Choose username: ").strip()
            email = input("Email (optional): ").strip() or None
            senatair_id = self.auth.create_senatair(username, email)
            if senatair_id:
                self.current_senatair = self.auth.get_senatair(username)
                print(f"✅ Welcome to Senatai, {username}!")
                print(f"🎁 You start with {self.current_senatair['policaps']} Policaps")
                return True
            return False
            
        elif choice == "3":
            print("👋 Continuing as Guest (responses won't be saved)")
            return True
            
        else:
            print("❌ Invalid choice")
            return False
    
    def get_bill_summary(self, bill_id):
        """Get bill summary and text for context"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT b.number, b.short_title_en, bt.summary_en, bt.text_en
            FROM bills_bill b
            LEFT JOIN bills_billtext bt ON b.id = bt.bill_id
            WHERE b.id = %s
        """, (bill_id,))
        
        result = cur.fetchone()
        cur.close()
        
        if result:
            number, title, summary, full_text = result
            return {
                'number': number,
                'title': title or 'Untitled Bill',
                'summary': summary or 'No summary available',
                'text_preview': (full_text or '')[:300] + '...' if full_text and len(full_text) > 300 else (full_text or 'No text available')
            }
        return None
    
    def generate_openparliament_link(self, bill_number):
        """Generate a link to OpenParliament for this bill"""
        if bill_number:
            clean_number = bill_number.replace(' ', '-').lower()
            return f"https://openparliament.ca/bills/{clean_number}/"
        return "https://openparliament.ca/bills/"
    
    def extract_user_keywords(self, user_input):
        """Enhanced keyword extraction with semantic expansion"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT keyword, COUNT(*) as frequency
            FROM bill_keywords 
            GROUP BY keyword 
            ORDER BY frequency DESC 
            LIMIT 200
        """)
        common_keywords = {row[0] for row in cur.fetchall()}
        cur.close()
        
        words = re.findall(r'\b[a-z]{3,15}\b', user_input.lower())
        
        # Enhanced keyword expansion for common concerns
        keyword_expansions = {
            'cheaper': ['cost', 'price', 'affordable', 'economic', 'consumer', 'market'],
            'toys': ['consumer', 'product', 'safety', 'import', 'trade', 'goods'],
            'expensive': ['cost', 'price', 'inflation', 'economic', 'affordable'],
            'school': ['education', 'student', 'learning', 'teacher', 'curriculum'],
            'hospital': ['healthcare', 'medical', 'doctor', 'treatment', 'health'],
            'rent': ['housing', 'affordable', 'landlord', 'tenant', 'property'],
            'job': ['employment', 'work', 'economy', 'worker', 'business'],
            'remote': ['technology', 'digital', 'electronic', 'device'],
            'control': ['regulation', 'management', 'oversight', 'authority'],
            'truck': ['vehicle', 'transportation', 'commercial', 'shipping'],
            'rv': ['vehicle', 'recreational', 'transportation', 'travel']
        }
        
        user_keywords = []
        for word in words:
            if word in common_keywords:
                user_keywords.append(word)
            elif len(word) > 3 and word not in ['this', 'that', 'with', 'about', 'would', 'want', 'more', 'little', 'lot']:
                user_keywords.append(word)
            
            # Add expanded keywords for better matching
            if word in keyword_expansions:
                user_keywords.extend(keyword_expansions[word])
        
        return list(set(user_keywords))
    
    def find_relevant_bills(self, user_keywords, limit=5):
        """Find bills using pre-computed keywords with relevance scoring"""
        if not user_keywords:
            return []
            
        cur = self.conn.cursor()
        keyword_tuple = tuple(user_keywords)
        placeholders = ','.join(['%s'] * len(keyword_tuple))
        
        cur.execute(f"""
            SELECT 
                bk.bill_id,
                bk.bill_number, 
                b.short_title_en as title,
                COUNT(*) as match_count,
                AVG(COALESCE(bk.relevance_score, 0.5)) as avg_relevance,
                SUM(bk.frequency) as total_frequency,
                STRING_AGG(DISTINCT bk.keyword, ', ') as matched_keywords
            FROM bill_keywords bk
            JOIN bills_bill b ON bk.bill_id = b.id
            WHERE bk.keyword IN ({placeholders})
            GROUP BY bk.bill_id, bk.bill_number, b.short_title_en
            ORDER BY match_count DESC, total_frequency DESC, avg_relevance DESC
            LIMIT %s
        """, keyword_tuple + (limit,))
        
        results = []
        for row in cur.fetchall():
            # Get bill context for each result
            bill_context = self.get_bill_summary(row[0])
            
            results.append({
                'bill_id': row[0],
                'number': row[1],
                'title': row[2] or 'Untitled Bill',
                'match_score': row[3],
                'relevance': row[4],
                'total_frequency': row[5],
                'matched_keywords': row[6].split(', ') if row[6] else [],
                'summary': bill_context['summary'] if bill_context else 'No summary available',
                'text_preview': bill_context['text_preview'] if bill_context else 'No text available',
                'op_link': self.generate_openparliament_link(row[1]) if bill_context else None
            })
        
        cur.close()
        return results
    
    def get_bill_context(self, bill_id):
        """Get contextual information about a bill for better questions"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT keyword, keyword_type, frequency, relevance_score
            FROM bill_keywords
            WHERE bill_id = %s
            ORDER BY relevance_score DESC NULLS LAST, frequency DESC
            LIMIT 10
        """, (bill_id,))
        
        keywords = []
        for row in cur.fetchall():
            keywords.append({
                'keyword': row[0],
                'type': row[1],
                'frequency': row[2],
                'relevance': row[3] or 0.5
            })
        
        cur.close()
        return keywords
    
    def generate_contextual_questions(self, bill, bill_context, user_input):
        """Generate questions that use the actual bill content"""
        questions = []
        
        if not bill_context:
            return questions
        
        main_topics = [kw['keyword'] for kw in bill_context[:3]]
        
        # Emotional question based on bill topics
        emotions = ['concerned', 'hopeful', 'frustrated', 'optimistic', 'worried', 'supportive']
        emotion = random.choice(emotions)
        
        questions.append({
            'type': 'emotional',
            'text': f"How {emotion} does '{bill['title']}' make you feel about {main_topics[0]}?",
            'bill': bill['number'],
            'matched_keywords': bill['matched_keywords'],
            'summary': bill['summary'],
            'op_link': bill['op_link']
        })
        
        # Tradeoff question if we have multiple topics
        if len(main_topics) >= 2:
            questions.append({
                'type': 'tradeoff',
                'text': f"Should '{bill['title']}' prioritize {main_topics[0]} over {main_topics[1]}?",
                'bill': bill['number'],
                'matched_keywords': bill['matched_keywords'],
                'summary': bill['summary'],
                'op_link': bill['op_link']
            })
        
        # Impact question
        questions.append({
            'type': 'impact', 
            'text': f"How significant is the potential impact of '{bill['title']}' on issues you care about?",
            'bill': bill['number'],
            'matched_keywords': bill['matched_keywords'],
            'summary': bill['summary'],
            'op_link': bill['op_link']
        })
        
        return questions
    
    def get_session_stats(self):
        """Get statistics about the growing keyword database"""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(DISTINCT bill_id) FROM bill_keywords")
        bill_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM bill_keywords")
        keyword_count = cur.fetchone()[0]
        
        cur.close()
        return bill_count, keyword_count
    
    def save_response(self, question_data, answer):
        """Save response if user is authenticated"""
        if self.current_senatair and self.current_session:
            success = self.auth.save_response(
                self.current_senatair['id'],
                self.current_session,
                question_data,
                answer
            )
            if success:
                print("💾 Response saved to your profile")
            return success
        else:
            print("💡 Response not saved (guest mode)")
            return False
    
    def start_session(self):
        """Main survey session with authentication"""
        if not self.login_or_register():
            return
        
        # Start session if user is logged in
        if self.current_senatair:
            self.current_session = self.auth.start_session(self.current_senatair['id'])
            print(f"📊 Session started: #{self.current_session}")
        
        self.session_count += 1
        bill_count, keyword_count = self.get_session_stats()
        
        print("\n" + "🏛️" * 20)
        print(f"🏛️    SENATAI V4 - Session {self.session_count}    🏛️")
        if self.current_senatair:
            print(f"🏛️  User: {self.current_senatair['username']} • {bill_count} bills analyzed 🏛️")
        else:
            print(f"🏛️  Guest Mode • {bill_count} bills analyzed 🏛️")
        print("🏛️" * 20)
        
        prompts = [
            "🗳️  What's on your mind? We'll match it to analyzed legislation...",
            "💬  Speak freely - we've analyzed laws ready to connect to your concerns...", 
            "🎯  What issue matters to you? Instant law matching powered by AI...",
        ]
        
        prompt = random.choice(prompts)
        user_input = input(f"\n{prompt}\n\n> ")
        
        if not user_input.strip():
            print("💭 Every opinion shapes better laws - what's yours?")
            return
        
        print(f"\n🔍 Analyzing your concern...")
        
        # Extract and match keywords
        user_keywords = self.extract_user_keywords(user_input)
        print(f"🎯 Your concerns: {user_keywords}")
        
        relevant_bills = self.find_relevant_bills(user_keywords)
        
        if not relevant_bills:
            print("🤔 No direct matches found with current legislation.")
            print("💡 Try rephrasing with more specific policy terms like:")
            print("   - 'consumer protection' instead of 'cheaper toys'")
            print("   - 'education funding' instead of 'better schools'") 
            print("   - 'healthcare access' instead of 'doctor visits'")
            return
        
        print(f"\n📚 Found {len(relevant_bills)} relevant laws:")
        for i, bill in enumerate(relevant_bills, 1):
            print(f"\n   {i}. 📋 {bill['number']}: {bill['title']}")
            if bill['op_link']:
                print(f"      🔗 {bill['op_link']}")
            print(f"      📝 Summary: {bill['summary'][:150]}...")
            print(f"      🎯 Matches: {', '.join(bill['matched_keywords'][:5])}")
        
        # Generate and ask questions
        questions = []
        for bill in relevant_bills[:2]:  # Top 2 most relevant
            bill_context = self.get_bill_context(bill['bill_id'])
            bill_questions = self.generate_contextual_questions(bill, bill_context, user_input)
            questions.extend(bill_questions)
        
        if not questions:
            print("🤷 Couldn't generate specific questions for these matches.")
            return
        
        print(f"\n📝 Generated {len(questions)} questions based on law analysis:")
        
        # Ask questions and save responses
        answers = []
        for i, q in enumerate(questions, 1):
            print(f"\n--- Question {i} ---")
            print(f"❓ {q['text']}")
            print(f"📋 Bill: {q.get('bill', 'Unknown')}")
            print(f"📝 Context: {q.get('summary', 'No summary available')[:100]}...")
            if q.get('op_link'):
                print(f"🔗 Learn more: {q['op_link']}")
            
            # Define options based on question type
            if q['type'] == 'emotional':
                options = ['Very ' + q['text'].split()[1], 'Somewhat ' + q['text'].split()[1], 'Neutral', 'Not ' + q['text'].split()[1]]
            elif q['type'] == 'tradeoff':
                parts = q['text'].split(' prioritize ')[1].split(' over ')
                options = [f'Yes, prioritize {parts[0]}', f'No, prioritize {parts[1].replace("?", "")}', 'Find balanced approach', 'Oppose either approach']
            else:  # impact
                options = ['Very significant', 'Somewhat significant', 'Minimal impact', 'Unsure']
            
            for j, opt in enumerate(options, 1):
                print(f"   {j}. {opt}")
            
            while True:
                answer = input("\nYour choice (1-4 or 'skip'): ").strip().lower()
                if answer in ['1', '2', '3', '4']:
                    selected = options[int(answer)-1]
                    print(f"💡 Recorded: {selected}")
                    
                    # Save the response if authenticated
                    self.save_response(q, selected)
                    
                    answers.append({
                        'question': q['text'],
                        'answer': selected,
                        'bill': q.get('bill', 'general')
                    })
                    break
                elif answer in ['skip', 's']:
                    print("💡 Question skipped")
                    break
                elif answer in ['quit', 'exit', 'q']:
                    return answers
                else:
                    print("❌ Please enter 1-4 or 'skip'")
        
        # Session summary
        policaps = len([a for a in answers if a['answer'] != 'skipped'])
        print(f"\n🎉 Session complete! +{policaps} Policaps earned!")
        
        if self.current_senatair:
            stats = self.auth.get_senatair_stats(self.current_senatair['id'])
            print(f"📈 Your profile: {stats['policaps']} Policaps • {stats['total_responses']} Responses")
        
        print("💡 Your responses help train our legislative matching system.")
        
        return answers
    
    def run_continuous(self):
        """Run continuous survey sessions"""
        print("🚀 Starting Adaptive Survey V4 with Context")
        print("💡 Now with bill summaries and OpenParliament links!")
        print("⏸️  Type 'quit' at any time to exit\n")
        
        total_sessions = 0
        while True:
            try:
                answers = self.start_session()
                total_sessions += 1
                
                if answers is None:  # User quit
                    break
                
                continue_prompt = input("\n🔁 Start another session? (y/n): ").strip().lower()
                if continue_prompt not in ['y', 'yes']:
                    break
                    
            except KeyboardInterrupt:
                print(f"\n🛑 Stopped after {total_sessions} sessions")
                break
            except Exception as e:
                print(f"❌ Session error: {e}")
                # Reset connection on error
                try:
                    self.conn.close()
                except:
                    pass
                self.conn = psycopg2.connect(
                    dbname="openparliament",
                    user="dan",
                    password="senatai2025", 
                    host="localhost"
                )
                continue
        
        self.end_session()
        print(f"\n👋 Thanks for using Senatai V4! Completed {total_sessions} sessions.")
    
    def end_session(self):
        """Properly end the session"""
        try:
            if self.current_session and hasattr(self.auth, 'conn') and not self.auth.conn.closed:
                self.auth.end_session(self.current_session)
        except Exception as e:
            print(f"⚠️  Session end warning: {e}")
        
        try:
            if hasattr(self, 'auth'):
                self.auth.close()
        except:
            pass
        
        try:
            if hasattr(self, 'conn') and not self.conn.closed:
                self.conn.close()
        except:
            pass

# Run the V4 survey
if __name__ == "__main__":
    survey = AdaptiveSurveyV4()
    try:
        survey.run_continuous()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        survey.end_session()
