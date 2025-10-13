import psycopg2
import spacy
from spacy.tokens import Doc

# Connect to the database
conn = psycopg2.connect(
    dbname="openparliament",
    user="postgres",
    password="senatai2025",
    host="localhost"
)
cur = conn.cursor()

# Query recent bills for text (uses schema indexes on latest_debate_date, session_id)
cur.execute("""
    SELECT short_title_en, summary_en 
    FROM bills_bill 
    WHERE summary_en IS NOT NULL 
      AND latest_debate_date >= '2020-01-01'  -- Focus on recent for testing
    ORDER BY latest_debate_date DESC 
    LIMIT 5  -- Smaller for old hardware
""")
rows = cur.fetchall()

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

# Process each row
for row in rows:
    title, summary = row
    text = f"{short_title_en or ''} {summary_en or ''}".strip()
    if not text:
        continue
    doc = nlp(text)
    
    # Extract entities (e.g., ORG, GPE for topics like trade agreements)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    
    # Clause detection (probes for legal structures like subsections)
    clauses = []
    for sent in doc.sents:
        sent_text = sent.text.strip()
        if any(keyword in sent_text.lower() for keyword in ['subsection', 'paragraph', 'article', 'clause', 'section']):
            clauses.append(sent_text)
    
    print(f"Bill: {short_title_en[:50]}...")
    print(f"Text Preview: {text[:150]}...")
    print(f"Entities: {entities}")
    print(f"Clauses Found: {len(clauses)}")
    for clause in clauses[:2]:  # Limit output
        print(f"  - {clause}")
    print("---")

# Close connection
cur.close()
conn.close()
