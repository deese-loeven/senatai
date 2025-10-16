# working_extractor.py
import spacy
import psycopg2
from collections import Counter

class WorkingExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.conn = psycopg2.connect(
            dbname="openparliament",
            user="postgres", 
            password="senatai2025",
            host="localhost"
        )
    
    def get_bills_simple(self, limit=5):
        """Simplest possible query that definitely works"""
        cur = self.conn.cursor()
        
        # Just get bill titles first - this should definitely work
        cur.execute("""
            SELECT id, number, short_title_en 
            FROM bills_bill 
            WHERE short_title_en IS NOT NULL AND short_title_en != ''
            ORDER BY latest_debate_date DESC NULLS LAST
            LIMIT %s
        """, (limit,))
        
        bills = []
        for row in cur.fetchall():
            bill_id, number, title = row
            keywords = self.extract_keywords(title)
            bills.append({
                'bill_id': bill_id,
                'number': number,
                'title': title,
                'keywords': keywords
            })
            print(f"✅ Found bill: {number} - {title}")
        
        cur.close()
        return bills
    
    def extract_keywords(self, text):
        """Extract keywords from text"""
        if not text:
            return []
        
        doc = self.nlp(text)
        keywords = [token.lemma_.lower() for token in doc 
                   if token.is_alpha and not token.is_stop 
                   and token.pos_ in ['NOUN', 'PROPN', 'ADJ']]
        
        return Counter(keywords).most_common(5)
    
    def extract_from_user(self, user_text):
        """Extract from user input"""
        return self.extract_keywords(user_text)
    
    def close(self):
        self.conn.close()

# Test
def test_working():
    extractor = WorkingExtractor()
    try:
        print("🚀 Testing simple bill extraction...")
        bills = extractor.get_bills_simple(3)
        
        print(f"\n📋 Found {len(bills)} bills:")
        for bill in bills:
            print(f"  - {bill['number']}: {bill['title']}")
            print(f"    Keywords: {[kw[0] for kw in bill['keywords']]}")
        
        # Test with user input
        user_keywords = extractor.extract_from_user("housing and rent prices are too high")
        print(f"\n🔍 User keywords: {user_keywords}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        extractor.close()

if __name__ == "__main__":
    test_working()
