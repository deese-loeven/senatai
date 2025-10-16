# batch_keyword_extractor3.py
import spacy
import psycopg2
from collections import Counter
import time
import sys
import signal

class BatchExtractorV3:
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
        
        # Custom stopwords to filter out formatting artifacts
        self.custom_stopwords = {
            'column', 'table', 'row', 'section', 'subsection', 'clause',
            'html', 'div', 'span', 'class', 'style', 'id', 'href', 'src',
            'paragraph', 'subparagraph', 'chapter', 'article', 'schedule',
            'annex', 'appendix', 'footer', 'header', 'nav', 'menu', 'button',
            'form', 'input', 'label', 'select', 'option', 'textarea', 'fieldset',
            'legend', 'iframe', 'frame', 'frameset', 'object', 'embed', 'param',
            'base', 'link', 'meta', 'script', 'noscript', 'canvas', 'svg', 'path',
            'rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'text',
            'g', 'defs', 'symbol', 'use', 'image', 'pattern', 'clip', 'mask',
            'marker', 'view', 'animate', 'set', 'animateMotion', 'animateTransform',
            'discard', 'mpath', 'foreignObject', 'desc', 'title', 'metadata'
        }
        
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        print(f"\n🛑 Shutting down gracefully...")
        self.running = False
    
    def extract_meaningful_keywords(self, bill_data):
        """Extract meaningful keywords with better filtering"""
        bill_id, number, short_title, summary, full_text = bill_data
        
        # Combine text sources
        text_parts = []
        if short_title:
            text_parts.append(short_title)
        if summary:
            text_parts.append(summary)
        if full_text:
            # Take first 8000 chars for better coverage but limit processing time
            text_parts.append(full_text[:8000])
        
        text = " ".join(text_parts).strip()
        
        if not text or len(text) < 100:
            return []
        
        doc = self.nlp(text)
        keywords = []
        
        # Extract meaningful nouns and proper nouns
        nouns = [token.lemma_.lower() for token in doc 
                if token.pos_ in ['NOUN', 'PROPN'] 
                and not token.is_stop 
                and token.lemma_.lower() not in self.custom_stopwords
                and len(token.text) > 2
                and len(token.lemma_) <= 30
                and token.is_alpha
                and not token.like_num]
        
        # Extract meaningful adjectives
        adjectives = [token.lemma_.lower() for token in doc 
                     if token.pos_ == 'ADJ'
                     and not token.is_stop
                     and token.lemma_.lower() not in self.custom_stopwords
                     and len(token.text) > 3
                     and len(token.lemma_) <= 30
                     and token.is_alpha]
        
        # Extract meaningful entities
        entities = [(ent.text.lower().replace('\n', ' ').replace('\t', ' '), ent.label_) 
                   for ent in doc.ents 
                   if ent.label_ in ['ORG', 'GPE', 'PERSON', 'LAW', 'EVENT', 'WORK_OF_ART']
                   and len(ent.text) <= 50
                   and not any(stopword in ent.text.lower() for stopword in self.custom_stopwords)]
        
        # Count frequencies
        noun_counter = Counter(nouns)
        adj_counter = Counter(adjectives)
        
        # Add high-quality nouns (top 12)
        for noun, freq in noun_counter.most_common(12):
            if freq >= 2:  # Only include words that appear multiple times
                keywords.append({
                    'bill_id': bill_id,
                    'bill_number': number,
                    'keyword': noun,
                    'type': 'noun',
                    'frequency': freq,
                    'relevance': min(freq / 4.0, 1.0)
                })
        
        # Add high-quality adjectives (top 8)
        for adj, freq in adj_counter.most_common(8):
            if freq >= 2:
                keywords.append({
                    'bill_id': bill_id,
                    'bill_number': number,
                    'keyword': adj,
                    'type': 'adjective', 
                    'frequency': freq,
                    'relevance': min(freq / 3.0, 1.0)
                })
        
        # Add meaningful entities (limit duplicates)
        seen_entities = set()
        for entity_text, entity_type in entities:
            if entity_text not in seen_entities and len(entity_text) > 3:
                seen_entities.add(entity_text)
                keywords.append({
                    'bill_id': bill_id,
                    'bill_number': number,
                    'keyword': entity_text,
                    'type': f'entity_{entity_type.lower()}',
                    'frequency': 1,
                    'relevance': 0.7
                })
                if len(seen_entities) >= 8:
                    break
        
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
                print(f"⚠️  Skipped keyword '{keyword_data['keyword']}': {e}")
                continue
        
        return success_count > 0
    
    def process_batch(self, batch_size=2):
        """Process bills with focus on quality over quantity"""
        cur = self.source_conn.cursor()
        cur.execute("""
            SELECT b.id, b.number, b.short_title_en, bt.summary_en, bt.text_en
            FROM bills_bill b
            LEFT JOIN bills_billtext bt ON b.id = bt.bill_id
            WHERE b.id NOT IN (SELECT DISTINCT bill_id FROM bill_keywords)
            AND (bt.summary_en IS NOT NULL OR bt.text_en IS NOT NULL)
            ORDER BY b.latest_debate_date DESC NULLS LAST
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
            print(f"🔍 Processing {number}: {title[:60]}..." if title else f"🔍 Processing {number}...")
            
            try:
                keywords = self.extract_meaningful_keywords(bill)
                if keywords:
                    success = self.save_keywords_safely(keywords)
                    if success:
                        self.processed_count += 1
                        processed += 1
                        print(f"✅ {number}: Saved {len(keywords)} meaningful keywords (Total: {self.processed_count})")
                        # Show sample of extracted keywords
                        sample_keywords = [k['keyword'] for k in keywords[:5]]
                        print(f"   Sample: {', '.join(sample_keywords)}")
                    else:
                        print(f"⚠️  {number}: No keywords saved due to errors")
                else:
                    print(f"⚠️  {number}: No meaningful keywords extracted")
                
                time.sleep(1.5)  # Slightly longer delay between bills
                
            except Exception as e:
                print(f"❌ Error with {number}: {e}")
                continue
        
        return processed
    
    def run_continuous(self):
        print("🚀 Starting BATCH KEYWORD EXTRACTOR V3...")
        print("🎯 Features: Better filtering, meaningful keywords only")
        print("⛔ Filtered: HTML artifacts, formatting words, low-frequency terms")
        print("⏸️  Press Ctrl+C to stop\n")
        
        total_processed = 0
        while self.running:
            try:
                processed = self.process_batch(2)  # Smaller batches for quality
                total_processed += processed
                
                if processed > 0:
                    print(f"📊 Progress: {total_processed} bills processed total\n")
                
                if self.running:
                    print("💤 Sleeping 25 seconds...")
                    time.sleep(25)
                    
            except Exception as e:
                print(f"❌ Batch error: {e}")
                time.sleep(30)
    
    def close(self):
        self.source_conn.close()
        self.target_conn.close()

if __name__ == "__main__":
    extractor = BatchExtractorV3()
    try:
        extractor.run_continuous()
    finally:
        extractor.close()
