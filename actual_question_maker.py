# fast_question_maker_v2.py
import psycopg2
import random

class FastQuestionMakerV2:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="openparliament",
            user="dan",
            password="senatai2025",
            host="localhost"
        )
    
    def find_relevant_bills(self, user_keywords, limit=5):
        """Fast matching using pre-computed keywords"""
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
                AVG(bk.relevance_score) as avg_relevance,
                STRING_AGG(DISTINCT bk.keyword, ', ') as matched_keywords
            FROM bill_keywords bk
            JOIN bills_bill b ON bk.bill_id = b.id
            WHERE bk.keyword IN ({placeholders})
            GROUP BY bk.bill_id, bk.bill_number, b.short_title_en
            ORDER BY match_count DESC, avg_relevance DESC
            LIMIT %s
        """, keyword_tuple + (limit,))
        
        results = []
        for row in cur.fetchall():
            results.append({
                'bill_id': row[0],
                'number': row[1],
                'title': row[2],
                'match_score': row[3],
                'relevance': row[4] or 0.5,
                'matched_keywords': row[5].split(', ') if row[5] else []
            })
        
        cur.close()
        return results
    
    def generate_questions_from_bills(self, relevant_bills, user_input):
        """Generate questions based on matched bills"""
        questions = []
        
        for bill in relevant_bills[:3]:  # Top 3 matches
            # Get detailed keywords for this bill
            cur = self.conn.cursor()
            cur.execute("""
                SELECT keyword, frequency, relevance_score
                FROM bill_keywords
                WHERE bill_id = %s
                ORDER BY relevance_score DESC, frequency DESC
                LIMIT 8
            """, (bill['bill_id'],))
            
            bill_keywords = [row[0] for row in cur.fetchall()]
            cur.close()
            
            if bill_keywords:
                # Emotional question
                emotions = ['concerned', 'hopeful', 'frustrated', 'optimistic']
                emotion = random.choice(emotions)
                questions.append({
                    'text': f"How {emotion} does '{bill['title']}' make you feel about {user_input.split()[0]}?",
                    'type': 'emotional',
                    'bill': bill['number'],
                    'options': [f'Very {emotion}', f'Somewhat {emotion}', 'Neutral', f'Not {emotion}']
                })
                
                # Factual question using actual bill keywords
                if len(bill_keywords) >= 2:
                    questions.append({
                        'text': f"Should '{bill['title']}' prioritize {bill_keywords[0]} over {bill_keywords[1]}?",
                        'type': 'tradeoff', 
                        'bill': bill['number'],
                        'options': [
                            f'Yes, prioritize {bill_keywords[0]}',
                            f'No, prioritize {bill_keywords[1]}',
                            'Find balanced approach',
                            'Oppose the bill entirely'
                        ]
                    })
        
        return questions
    
    def close(self):
        self.conn.close()

# Test the V2 question maker
def test_v2_questions():
    maker = FastQuestionMakerV2()
    
    test_inputs = [
        "housing costs are too high",
        "climate change concerns me",
        "healthcare access needs improvement",
        "education funding is inadequate"
    ]
    
    for user_input in test_inputs:
        print(f"\n🎯 User: '{user_input}'")
        
        # Simple keyword extraction
        user_keywords = [word for word in user_input.lower().split() 
                        if len(word) > 3 and word not in ['about', 'that', 'this', 'with', 'are', 'too']]
        
        print(f"🔍 Searching for bills matching: {user_keywords}")
        
        relevant_bills = maker.find_relevant_bills(user_keywords)
        print(f"📚 Found {len(relevant_bills)} relevant bills")
        
        for bill in relevant_bills:
            print(f"   📋 {bill['number']}: {bill['title']}")
            print(f"      Matches: {bill['matched_keywords']}")
        
        questions = maker.generate_questions_from_bills(relevant_bills, user_input)
        print(f"📝 Generated {len(questions)} questions:")
        
        for i, q in enumerate(questions, 1):
            print(f"  {i}. {q['text']}")
            for j, opt in enumerate(q.get('options', []), 1):
                print(f"     {j}. {opt}")
    
    maker.close()

if __name__ == "__main__":
    test_v2_questions()
