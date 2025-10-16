import spacy
import psycopg2
from collections import Counter

nlp = spacy.load("en_core_web_sm")

conn = psycopg2.connect(
    dbname="openparliament",
    user="postgres",
    password="senatai2025",
    host="localhost"
 )
cur = conn.cursor()

cur.execute("""
    SELECT 
        b.id,
        b.number,
        b.short_title_en,
        bt.summary_en,
        bt.text_en
    FROM bills_bill b
    JOIN bills_billtext bt ON b.id = bt.bill_id
    WHERE bt.text_en != ''
    LIMIT 3;
""")

for row in cur.fetchall():
    bill_id, number, short_title, summary, full_text = row
    
    print(f"\n{'='*80}")
    print(f"Bill {number}: {short_title}")
    print(f"{'='*80}")
    
    # Analyze summary
    doc = nlp(summary[:5000])
    
    keywords = [token.lemma_.lower() for token in doc 
                if token.pos_ in ['NOUN', 'PROPN'] 
                and not token.is_stop 
                and len(token.text) > 2]
    
    print(f"Keywords: {Counter(keywords).most_common(10)}")
    print(f"Entities: {[(ent.text, ent.label_) for ent in doc.ents][:10]}")

conn.close()

