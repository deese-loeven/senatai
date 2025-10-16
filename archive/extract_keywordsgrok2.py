import spacy
import psycopg2
from collections import Counter

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

# Connect to the database
conn = psycopg2.connect(
    dbname="openparliament",
    user="postgres",
    password="senatai2025",
    host="localhost"
)
cur = conn.cursor()

# Enhanced query: Join billtext for full text if summary empty
cur.execute("""
    SELECT 
        b.id,
        b.short_title_en,
        COALESCE(bt.summary_en, bt.long_title) AS text_summary,
        bt.full_text
    FROM bills_bill b
    LEFT JOIN bills_billtext bt ON b.id = bt.bill_id
    WHERE b.summary_en IS NOT NULL OR b.long_title IS NOT NULL OR bt.full_text IS NOT NULL
    ORDER BY b.latest_debate_date DESC NULLS LAST
    LIMIT 5
""")
rows = cur.fetchall()

# Process each row
for row in rows:
    bill_id, short_title_en, text_summary, full_text = row
    # Combine text (truncate full_text for perf on old hardware)
    text = f"{short_title_en or ''} {text_summary or ''} {full_text[:2000] or ''}".strip()
    if not text:
        print(f"Bill {bill_id}: No text available.")
        continue
    
    # Debug: Check text loading
    print(f"Debug - Bill {bill_id} text length: {len(text)} chars")
    print(f"Debug - Sample text: {text[:100]}...")
    
    doc = nlp(text)
    
    # Extract entities (NER: focus on relevant labels)
    entities = [(ent.text, ent.label_) for ent in doc.ents if ent.label_ in ['ORG', 'GPE', 'LAW', 'PERSON']]
    unique_entities = list(set(entities))[:5]
    
    # Extract keywords: nouns, proper nouns, adjectives
    keywords = [token.text.lower() for token in doc if token.is_alpha and not token.is_stop and token.pos_ in ['NOUN', 'PROPN', 'ADJ']]
    bill_counter = Counter(keywords)
    unique_keywords = [word for word, _ in bill_counter.most_common(10)]
    
    # Your "boxes" output
    print("=" * 80)
    print(f"Bill {short_title_en or bill_id}:")
    print("=" * 80)
    print(f"Keywords: {unique_keywords}")
    print(f"Entities: {unique_entities}")
    print("")

# Close connection
cur.close()
conn.close()
