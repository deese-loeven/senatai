# adaptive_survey_v3.py
import psycopg2
import random
import re
from collections import Counter

class AdaptiveSurveyV3:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="openparliament",
            user="dan",
            password="senatai2025", 
            host="localhost"
        )
        self.session_count = 0
        
    def extract_user_keywords(self, user_input):
        """Better keyword extraction that learns from your bill database"""
        # Get common keywords from database to inform extraction
        cur = self.conn.cursor()
        cur.execute("""
            SELECT keyword, COUNT(*) as frequency
            FROM bill_keywords 
            GROUP BY keyword 
            ORDER BY frequency DESC 
            LIMIT 100
        """)
        common_keywords = {row[0] for row in cur.fetchall()}
        cur.close()
        
        # Extract words from user input
        words = re.findall(r'\b[a-z]{3,15}\b', user_input.lower())
        
        # Prioritize words that appear in legislation
        user_keywords = []
        for word in words:
            if word in common_keywords:
                user_keywords.append(word)  # High priority - exists in bills
            elif len(word) > 4 and word not in ['this', 'that', 'with', 'about', 'would']:
                user_keywords.append(word)  # Medium priority - substantive word
        
        return list(set(user_keywords))  # Remove duplicates
    
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
            results.append({
                'bill_id': row[0],
                'number': row[1],
                'title': row[2],
                'match_score': row[3],
                'relevance': row[4],
                'total_frequency': row[5],
                'matched_keywords': row[6].split(', ') if row[6] else []
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
            'options': [f'Very {emotion}', f'Somewhat {emotion}', 'Neutral', f'Not {emotion}']
        })
        
        # Tradeoff question if we have multiple topics
        if len(main_topics) >= 2:
            questions.append({
                'type': 'tradeoff',
                'text': f"Should '{bill['title']}' prioritize {main_topics[0]} over {main_topics[1]}?",
                'bill': bill['number'],
                'options': [
                    f'Yes, prioritize {main_topics[0]}',
                    f'No, prioritize {main_topics[1]}',
                    'Find balanced approach',
                    'Oppose either approach'
                ]
            })
        
        # Impact question
        questions.append({
            'type': 'impact',
            'text': f"How significant is the potential impact of '{bill['title']}' on issues you care about?",
            'bill': bill['number'],
            'options': ['Very significant', 'Somewhat significant', 'Minimal impact', 'Unsure']
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
    
    def start_session(self):
        self.session_count += 1
        bill_count, keyword_count = self.get_session_stats()
        
        print("\n" + "🏛️" * 20)
        print(f"🏛️    SENATAI V3 - Session {self.session_count}    🏛️")
        print(f"🏛️  {bill_count} bills • {keyword_count} keywords analyzed  🏛️")
        print("🏛️" * 20)
        
        prompts = [
            "🗳️  What's on your mind? We'll match it to analyzed legislation...",
            "💬  Speak freely - we've analyzed laws ready to connect to your concerns...", 
            "🎯  What issue matters to you? Instant law matching powered by AI...",
            "📢  Your voice matters - we'll find relevant laws automatically..."
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
            print("💡 Your concern is still recorded and will help improve future matching!")
            return
        
        print(f"\n📚 Found {len(relevant_bills)} relevant laws:")
        for bill in relevant_bills:
            print(f"   📋 {bill['number']}: {bill['title']}")
            print(f"      Matches: {', '.join(bill['matched_keywords'][:3])}")
        
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
        
        # Ask questions
        answers = []
        for i, q in enumerate(questions, 1):
            print(f"\n--- Question {i} ---")
            print(f"❓ {q['text']}")
            
            if 'options' in q:
                for j, opt in enumerate(q['options'], 1):
                    print(f"   {j}. {opt}")
            
            while True:
                answer = input("\nYour choice (1-4 or 'skip'): ").strip().lower()
                if answer in ['1', '2', '3', '4']:
                    selected = q['options'][int(answer)-1]
                    print(f"💡 Recorded: {selected}")
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
        print("💡 Your responses help train our legislative matching system.")
        
        return answers
    
    def run_continuous(self):
        """Run continuous survey sessions"""
        print("🚀 Starting Adaptive Survey V3")
        print("💡 Using pre-analyzed legislation database")
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
                continue
        
        print(f"\n👋 Thanks for using Senatai V3! Completed {total_sessions} sessions.")
    
    def close(self):
        self.conn.close()

# Run the V3 survey
if __name__ == "__main__":
    survey = AdaptiveSurveyV3()
    try:
        survey.run_continuous()
    finally:
        survey.close()
