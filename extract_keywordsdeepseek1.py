# keyword_extractor.py
import spacy
import psycopg2
from collections import Counter

class LegislationExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.conn = psycopg2.connect(
            dbname="openparliament",
            user="postgres", 
            password="senatai2025",
            host="localhost"
        )
    
    def extract_from_bill(self, bill_id=None, limit=5):
        """Extract keywords and entities from bills"""
        cur = self.conn.cursor()
        
        if bill_id:
            # Extract from specific bill
            cur.execute("""
                SELECT b.id, b.short_title_en, b.summary_en, bt.full_text
                FROM bills_bill b
                LEFT JOIN bills_billtext bt ON b.id = bt.bill_id
                WHERE b.id = %s
            """, (bill_id,))
        else:
            # Extract from recent bills
            cur.execute("""
                SELECT b.id, b.short_title_en, b.summary_en, bt.full_text
                FROM bills_bill b
                LEFT JOIN bills_billtext bt ON b.id = bt.bill_id
                WHERE b.summary_en IS NOT NULL OR bt.full_text IS NOT NULL
                ORDER BY b.latest_debate_date DESC NULLS LAST
                LIMIT %s
            """, (limit,))
        
        bills_data = []
        for row in cur.fetchall():
            bill_id, short_title, summary, full_text = row
            text = f"{short_title or ''} {summary or ''} {full_text[:2000] or ''}".strip()
            
            if not text:
                continue
                
            doc = self.nlp(text)
            
            # Extract entities
            entities = [(ent.text, ent.label_) for ent in doc.ents 
                       if ent.label_ in ['ORG', 'GPE', 'LAW', 'PERSON', 'MONEY', 'DATE']]
            
            # Extract keywords
            keywords = [token.lemma_.lower() for token in doc 
                       if token.is_alpha and not token.is_stop 
                       and token.pos_ in ['NOUN', 'PROPN', 'ADJ', 'VERB']]
            
            bill_data = {
                'bill_id': bill_id,
                'title': short_title,
                'keywords': Counter(keywords).most_common(15),
                'entities': list(set(entities))[:10],
                'summary': summary,
                'full_text_preview': text[:500]  # For context
            }
            bills_data.append(bill_data)
        
        cur.close()
        return bills_data
    
    def extract_from_user_input(self, user_text):
        """Extract keywords from user's natural language input"""
        doc = self.nlp(user_text)
        
        user_keywords = [token.lemma_.lower() for token in doc 
                        if token.is_alpha and not token.is_stop 
                        and token.pos_ in ['NOUN', 'PROPN', 'ADJ', 'VERB']]
        
        user_entities = [(ent.text, ent.label_) for ent in doc.ents]
        
        return {
            'keywords': list(set(user_keywords)),
            'entities': user_entities,
            'sentiment': self.analyze_sentiment(user_text)
        }
    
    def analyze_sentiment(self, text):
        """Simple sentiment analysis - you can enhance this later"""
        positive_words = ['good', 'great', 'love', 'hope', 'support', 'better']
        negative_words = ['bad', 'terrible', 'hate', 'angry', 'frustrated', 'worse']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        else:
            return 'neutral'

    def close(self):
        self.conn.close()
