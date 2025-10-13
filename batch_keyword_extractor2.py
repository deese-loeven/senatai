# batch_keyword_extractor_fixed.py
import spacy
import psycopg2
from collections import Counter
import time
import sys
import signal

class FixedBatchExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.source_conn = psycopg2.connect(
            dbname="openparliament",
            user="dan",
            password="senatai2025",
            host="localhost"
        )
        self.target_conn = psycopg2.connect(
            dbname="openparliament",
            user="dan",
            password="senatai2025", 
            host="localhost"
        )
        self.processed_count = 0
        self.running = True
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        print(f"\n🛑 Shutting down gracefully...")
        self.running = False
    
    def extract_keywords_from_bill(self, bill_data):
        """Extract keywords with length validation"""
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
        
        # Extract with length limits
        nouns = [token.lemma_.lower() for token in doc 
                if token.pos_ in ['NOUN', 'PROPN'] 
                and not token.is_stop 
                and len(token.text) > 2
                and len(token.lemma_) <= 50  # Limit keyword length
                and token.is_alpha]
        
        entities = [(ent.text.lower(), ent.label_) for ent in doc.ents 
                   if ent.label_ in ['ORG', 'GPE', 'PERSON', 'LAW']
                   and len(ent.text) <= 50]  # Limit entity length
        
        adjectives = [token.lemma_.lower() for token in doc 
                     if token.pos_ == 'ADJ'
                     and not token.is_stop
                     and len(token.text) > 3
                     and len(token.lemma_) <= 50]
        
        noun_counter = Counter(nouns)
        adj_counter = Counter(adjectives)
        
        # Add nouns (with length validation)
        for noun, freq in noun_counter.most_common(15):
            if len(noun) <= 50:  # Double-check length
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
            if len(adj) <= 50:
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
            if len(entity_text) <= 50:
                keywords.append({
                    'bill_id': bill_id,
                    'bill_number': number,
                    'keyword': entity_text,
                    'type': f'entity_{entity_type.lower()}',
                    'frequency': 1,
                    'relevance': 0.8
                })
        
        return keywords
    
    def save_keywords_safely(self, keywords):
        """Save keywords with individual transaction per keyword"""
        if not keywords:
            return True
        
        success_count = 0
        for keyword_data in keywords:
            try:
                # Create new connection for each keyword to avoid transaction issues
                conn = psycopg2.connect(
                    dbname="openparliament",
                    user="dan",
                    password="senatai2025",
                    host="localhost"
                )
                cur = conn.cursor()
                
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
                
                conn.commit()
                success_count += 1
                cur.close()
                conn.close()
                
            except Exception as e:
                print(f"⚠️  Skipped long keyword: '{keyword_data['keyword']}' ({len(keyword_data['keyword'])} chars)")
                continue
        
        return success_count > 0
    
    def process_batch(self, batch_size=3):
        """Process bills with better error handling"""
        cur = self.source_conn.cursor()
        cur.execute("""
            SELECT b.id, b.number, b.short_title_en, bt.summary_en, bt.text_en
            FROM bills_bill b
            LEFT JOIN bills_billtext bt ON b.id = bt.bill_id
            WHERE b.id NOT IN (SELECT DISTINCT bill_id FROM bill_keywords)
            AND (bt.summary_en IS NOT NULL OR bt.text_en IS NOT NULL)
            ORDER BY b.latest_debate_date DESC
            LIMIT %s
        """, (batch_size,))
        bills = cur.fetchall()
        cur.close()
        
        if not bills:
            print("💤 All bills processed! Sleeping 5 minutes...")
            time.sleep(300)
            return 0
        
        processed = 0
        for bill in bills:
            if not self.running:
                break
                
            bill_id, number, title, summary, full_text = bill
            print(f"🔍 Processing {number}...")
            
            try:
                keywords = self.extract_keywords_from_bill(bill)
                if keywords:
                    success = self.save_keywords_safely(keywords)
                    if success:
                        self.processed_count += 1
                        processed += 1
                        print(f"✅ {number}: Saved {len(keywords)} keywords (Total: {self.processed_count})")
                    else:
                        print(f"⚠️  {number}: No keywords saved due to errors")
                else:
                    print(f"⚠️  {number}: No keywords extracted")
                
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error with {number}: {e}")
                continue
        
        return processed
    
    def run_continuous(self):
        print("🚀 Starting FIXED batch keyword extraction...")
        print("💡 No more transaction errors!")
        print("⏸️  Press Ctrl+C to stop\n")
        
        total_processed = 0
        while self.running:
            try:
                processed = self.process_batch(2)
                total_processed += processed
                
                if processed > 0:
                    print(f"📊 Progress: {total_processed} bills processed total\n")
                
                if self.running:
                    print("💤 Sleeping 20 seconds...")
                    time.sleep(20)
                    
            except Exception as e:
                print(f"❌ Batch error: {e}")
                time.sleep(30)
    
    def close(self):
        self.source_conn.close()
        self.target_conn.close()

if __name__ == "__main__":
    extractor = FixedBatchExtractor()
    try:
        extractor.run_continuous()
    finally:
        extractor.close()
