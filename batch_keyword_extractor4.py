# batch_keyword_extractor4.py
import spacy
import psycopg2
from collections import Counter
import time
import sys
import signal
import re

class BatchExtractorV4:
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
        
        # Enhanced stopwords and filters
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
        
        # Common legislative terms that are too generic
        self.generic_legislative_terms = {
            'act', 'bill', 'law', 'legislation', 'regulation', 'statute',
            'section', 'subsection', 'clause', 'paragraph', 'subparagraph',
            'chapter', 'part', 'division', 'schedule', 'annex', 'appendix',
            'amendment', 'provision', 'article', 'regulation', 'rule',
            'code', 'ordinance', 'by-law', 'bylaw', 'policy', 'directive'
        }
        
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        print(f"\n🛑 Shutting down gracefully...")
        self.running = False
    
    def calculate_normalized_relevance(self, frequency, total_words_in_bill, word_length):
        """Calculate normalized relevance score"""
        # Base frequency score (normalized by text length)
        freq_score = frequency / max(total_words_in_bill * 0.01, 10)
        
        # Word length bonus (prefer medium-length meaningful words)
        length_bonus = 1.0
        if 4 <= word_length <= 12:
            length_bonus = 1.2  # Ideal word length range
        elif word_length > 15:
            length_bonus = 0.7  # Very long words often less meaningful
            
        # Combine scores with cap at 1.0
        relevance = min(freq_score * length_bonus, 1.0)
        return round(relevance, 2)
    
    def extract_balanced_keywords(self, bill_data):
        """Extract balanced keywords with better normalization"""
        bill_id, number, short_title, summary, full_text = bill_data
        
        # Combine text sources
        text_parts = []
        if short_title:
            text_parts.append(short_title)
        if summary:
            text_parts.append(summary)
        if full_text:
            # Take reasonable sample of full text
            text_parts.append(full_text[:6000])
        
        text = " ".join(text_parts).strip()
        
        if not text or len(text) < 100:
            return []
        
        # Estimate total words for normalization
        total_words = len(text.split())
        
        doc = self.nlp(text)
        keywords = []
        
        # Extract meaningful nouns and proper nouns
        nouns = []
        for token in doc:
            if (token.pos_ in ['NOUN', 'PROPN'] and 
                not token.is_stop and
                token.lemma_.lower() not in self.custom_stopwords and
                token.lemma_.lower() not in self.generic_legislative_terms and
                len(token.text) > 2 and
                len(token.lemma_) <= 25 and
                token.is_alpha and
                not token.like_num):
                
                noun = token.lemma_.lower()
                # Filter out single letters and weird artifacts
                if re.match(r'^[a-z]{3,}$', noun):
                    nouns.append(noun)
        
        # Extract meaningful adjectives
        adjectives = []
        for token in doc:
            if (token.pos_ == 'ADJ' and
                not token.is_stop and
                token.lemma_.lower() not in self.custom_stopwords and
                len(token.text) > 3 and
                len(token.lemma_) <= 20 and
                token.is_alpha):
                
                adj = token.lemma_.lower()
                if re.match(r'^[a-z]{4,}$', adj):
                    adjectives.append(adj)
        
        # Extract meaningful entities with better filtering
        entities = []
        for ent in doc.ents:
            if (ent.label_ in ['ORG', 'GPE', 'PERSON', 'LAW', 'EVENT'] and
                len(ent.text) <= 40 and
                len(ent.text) >= 3 and
                not any(stopword in ent.text.lower() for stopword in self.custom_stopwords)):
                
                clean_entity = ent.text.lower().replace('\n', ' ').replace('\t', ' ').strip()
                if re.match(r'^[a-zA-Z0-9\s\-]{3,}$', clean_entity):
                    entities.append((clean_entity, ent.label_))
        
        # Count frequencies
        noun_counter = Counter(nouns)
        adj_counter = Counter(adjectives)
        
        # Add balanced nouns (focus on moderate frequencies)
        for noun, freq in noun_counter.most_common(15):
            if 2 <= freq <= 20:  # Avoid extremely high frequencies (likely artifacts)
                relevance = self.calculate_normalized_relevance(freq, total_words, len(noun))
                keywords.append({
                    'bill_id': bill_id,
                    'bill_number': number,
                    'keyword': noun,
                    'type': 'noun',
                    'frequency': freq,
                    'relevance': relevance
                })
        
        # Add balanced adjectives
        for adj, freq in adj_counter.most_common(8):
            if 2 <= freq <= 15:
                relevance = self.calculate_normalized_relevance(freq, total_words, len(adj))
                keywords.append({
                    'bill_id': bill_id,
                    'bill_number': number,
                    'keyword': adj,
                    'type': 'adjective', 
                    'frequency': freq,
                    'relevance': relevance
                })
        
        # Add meaningful entities (limit to most relevant)
        seen_entities = set()
        for entity_text, entity_type in entities:
            if entity_text not in seen_entities:
                seen_entities.add(entity_text)
                # Entities get moderate relevance by default
                keywords.append({
                    'bill_id': bill_id,
                    'bill_number': number,
                    'keyword': entity_text,
                    'type': f'entity_{entity_type.lower()}',
                    'frequency': 1,
                    'relevance': 0.6  # Lower default relevance for entities
                })
                if len(seen_entities) >= 6:
                    break
        
        return keywords
    
    def save_keywords_safely(self, keywords):
        """Save keywords with individual transaction per keyword"""
        if not keywords:
            return True
        
        success_count = 0
        for keyword_data in keywords:
            try:
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
        """Process bills with focus on balanced keyword extraction"""
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
            bill_desc = f"{number}: {title[:50]}..." if title else f"{number}"
            print(f"🔍 Processing {bill_desc}")
            
            try:
                keywords = self.extract_balanced_keywords(bill)
                if keywords:
                    success = self.save_keywords_safely(keywords)
                    if success:
                        self.processed_count += 1
                        processed += 1
                        print(f"✅ {number}: Saved {len(keywords)} balanced keywords (Total: {self.processed_count})")
                        # Show sample with relevance scores
                        sample_keywords = [f"{k['keyword']}({k['relevance']})" for k in keywords[:4]]
                        print(f"   Sample: {', '.join(sample_keywords)}")
                    else:
                        print(f"⚠️  {number}: No keywords saved due to errors")
                else:
                    print(f"⚠️  {number}: No balanced keywords extracted")
                
                time.sleep(1.5)
                
            except Exception as e:
                print(f"❌ Error with {number}: {e}")
                continue
        
        return processed
    
    def run_continuous(self):
        print("🚀 Starting BATCH KEYWORD EXTRACTOR V4...")
        print("🎯 Features: Balanced frequency, normalized relevance, better filtering")
        print("⛔ Filtered: Generic legislative terms, extreme frequencies, artifacts")
        print("📊 Shows: Keywords with relevance scores (0.0-1.0)")
        print("⏸️  Press Ctrl+C to stop\n")
        
        total_processed = 0
        while self.running:
            try:
                processed = self.process_batch(2)
                total_processed += processed
                
                if processed > 0:
                    print(f"📈 Progress: {total_processed} bills processed total\n")
                
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
    extractor = BatchExtractorV4()
    try:
        extractor.run_continuous()
    finally:
        extractor.close()
