# batch_keyword_extractor_fixed.py
import spacy
import psycopg2
from collections import Counter
import time
import sys
import signal

class BatchKeywordExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.source_conn = psycopg2.connect(
            dbname="openparliament",
            user="dan",  # ← Fixed: use your Linux username
            password="senatai2025",
            host="localhost"
        )
        self.target_conn = psycopg2.connect(
            dbname="openparliament",
            user="dan",  # ← Fixed: use your Linux username  
            password="senatai2025",
            host="localhost"
        )
        self.processed_count = 0
        self.running = True
        
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def create_keywords_table(self):
        """Create the keywords table if it doesn't exist"""
        cur = self.target_conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS bill_keywords (
                id SERIAL PRIMARY KEY,
                bill_id INTEGER NOT NULL,
                bill_number VARCHAR(50) NOT NULL,
                keyword VARCHAR(100) NOT NULL,
                keyword_type VARCHAR(20) NOT NULL,
                frequency INTEGER DEFAULT 1,
                relevance_score FLOAT DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(bill_id, keyword, keyword_type)
            )
        """)
        
        for idx in ['keyword', 'bill_id', 'keyword_type']:
            cur.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_{idx} 
                ON bill_keywords({idx})
            """)
        
        self.target_conn.commit()
        cur.close()
        print("✅ Keywords table ready")
    
    def get_bills_to_process(self, limit=10):
        """Get bills that haven't been processed yet"""
        cur = self.source_conn.cursor()
        cur.execute("""
            SELECT b.id, b.number, b.short_title_en, bt.summary_en, bt.text_en
            FROM bills_bill b
            LEFT JOIN bills_billtext bt ON b.id = bt.bill_id
            WHERE b.id NOT IN (SELECT DISTINCT bill_id FROM bill_keywords)
            AND (bt.summary_en IS NOT NULL OR bt.text_en IS NOT NULL)
            ORDER BY b.latest_debate_date DESC
            LIMIT %s
        """, (limit,))
        return cur.fetchall()
    
    def extract_keywords_from_bill(self, bill_data):
        """Extract keywords from a single bill"""
        bill_id, number, short_title, summary, full_text = bill_data
        
        text_parts = []
        if short_title:
            text_parts.append(short_title)
        if summary:
            text_parts.append(summary)
        if full_text:
            text_parts.append(full_text[:5000])
        
        text = " ".join(text_parts).strip()
        
        if not text or len(text) < 100:
            return []
        
        doc = self.nlp(text)
        
        keywords = []
        
        # Nouns and proper nouns
        nouns = [token.lemma_.lower() for token in doc 
                if token.pos_ in ['NOUN', 'PROPN'] 
                and not token.is_stop 
                and len(token.text) > 2
                and token.is_alpha]
        
        # Entities
        entities = [(ent.text.lower(), ent.label_) for ent in doc.ents 
                   if ent.label_ in ['ORG', 'GPE', 'PERSON', 'LAW']]
        
        # Adjectives
        adjectives = [token.lemma_.lower() for token in doc 
                     if token.pos_ == 'ADJ'
                     and not token.is_stop
                     and len(token.text) > 3]
        
        noun_counter = Counter(nouns)
        adj_counter = Counter(adjectives)
        
        # Add nouns
        for noun, freq in noun_counter.most_common(15):
            keywords.append({
                'bill_id': bill_id,
                'bill_number': number,
                'keyword': noun,
                'type': 'noun',
                'frequency': freq,
                'relevance': min(freq / 5.0, 1.0)
            })
        
        # Add adjectives
        for adj, freq in adj_counter.most_common(10):
            keywords.append({
                'bill_id': bill_id,
                'bill_number': number,
                'keyword': adj,
                'type': 'adjective', 
                'frequency': freq,
                'relevance': min(freq / 3.0, 1.0)
            })
        
        # Add entities
        for entity_text, entity_type in entities[:10]:
            keywords.append({
                'bill_id': bill_id,
                'bill_number': number,
                'keyword': entity_text,
                'type': f'entity_{entity_type.lower()}',
                'frequency': 1,
                'relevance': 0.8
            })
        
        return keywords
    
    def save_keywords(self, keywords):
        """Save keywords to database"""
        if not keywords:
            return
        
        cur = self.target_conn.cursor()
        for keyword_data in keywords:
            try:
                cur.execute("""
                    INSERT INTO bill_keywords 
                    (bill_id, bill_number, keyword, keyword_type, frequency, relevance_score)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (bill_id, keyword, keyword_type) 
                    DO UPDATE SET frequency = EXCLUDED.frequency,
                                  relevance_score = EXCLUDED.relevance_score
                """, (
                    keyword_data['bill_id'],
                    keyword_data['bill_number'],
                    keyword_data['keyword'],
                    keyword_data['type'],
                    keyword_data['frequency'],
                    keyword_data['relevance']
                ))
            except Exception as e:
                print(f"❌ Error saving keyword: {e}")
                continue
        
        self.target_conn.commit()
        cur.close()
    
    def process_batch(self, batch_size=5):
        """Process a batch of bills"""
        bills = self.get_bills_to_process(batch_size)
        
        if not bills:
            print("🎉 All bills processed! Sleeping for 1 hour...")
            time.sleep(3600)
            return 0
        
        processed = 0
        for bill in bills:
            if not self.running:
                break
                
            bill_id = bill[0]
            bill_number = bill[1]
            
            print(f"🔍 Processing {bill_number}...")
            
            try:
                keywords = self.extract_keywords_from_bill(bill)
                self.save_keywords(keywords)
                
                self.processed_count += 1
                processed += 1
                
                print(f"✅ {bill_number}: Added {len(keywords)} keywords "
                      f"(Total: {self.processed_count} bills)")
                
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ Error processing {bill_number}: {e}")
                continue
        
        return processed
    
    def run_continuous(self, batch_size=3, sleep_time=30):
        """Run continuously with low CPU usage"""
        print("🚀 Starting batch keyword extraction...")
        print("💡 Running at ~5% CPU - will process slowly in background")
        print("⏸️  Press Ctrl+C to stop gracefully")
        
        self.create_keywords_table()
        
        total_processed = 0
        while self.running:
            try:
                processed = self.process_batch(batch_size)
                total_processed += processed
                
                if processed > 0:
                    print(f"📊 Progress: {total_processed} bills processed total")
                
                if self.running:
                    print(f"💤 Sleeping for {sleep_time} seconds...")
                    time.sleep(sleep_time)
                    
            except Exception as e:
                print(f"❌ Batch processing error: {e}")
                time.sleep(60)
    
    def close(self):
        self.source_conn.close()
        self.target_conn.close()

def check_keywords_status():
    conn = psycopg2.connect(
        dbname="openparliament",
        user="dan",  # ← Fixed
        password="senatai2025",
        host="localhost"
    )
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(DISTINCT bill_id) FROM bill_keywords")
    processed_bills = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM bills_bill")
    total_bills = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM bill_keywords")
    total_keywords = cur.fetchone()[0]
    
    print(f"📊 Keywords Database Status:")
    print(f"   Processed bills: {processed_bills}/{total_bills}")
    print(f"   Total keywords: {total_keywords}")
    print(f"   Coverage: {(processed_bills/total_bills*100):.1f}%" if total_bills > 0 else "   Coverage: 0%")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        check_keywords_status()
    else:
        extractor = BatchKeywordExtractor()
        try:
            extractor.run_continuous(batch_size=3, sleep_time=30)
        finally:
            extractor.close()
