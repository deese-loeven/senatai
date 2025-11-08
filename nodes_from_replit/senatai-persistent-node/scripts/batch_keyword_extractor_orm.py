# ~/senatai/nodes_from_replit/senatai-persistent-node/scripts/batch_keyword_extractor_orm.py
import os
import sys
# --- ROBUST PATH FIX ---
# This guarantees the project root is in the path, regardless of where the script is launched from.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# -----------------------
import yaml
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from core.models import Base, LawContent, BillKeyword
import re
from core.models import Base, LawContent, BillKeyword

# --- Configuration & Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get database URI from environment variable (required for both app and scripts)
DATABASE_URI = os.environ.get('DATABASE_URL')
if not DATABASE_URI:
    logging.error("DATABASE_URL environment variable not set. Exiting.")
    exit(1)

# Initialize SQLAlchemy
try:
    engine = create_engine(DATABASE_URI)
    Session = sessionmaker(bind=engine)
    # Ensure new tables exist
    Base.metadata.create_all(engine)
    logging.info("Database engine and new tables (law_content, bill_keywords) initialized.")
except Exception as e:
    logging.error(f"Failed to connect to or initialize database: {e}")
    exit(1)

# Simple Mock Keyword Extraction Function (Replace with your actual NLP code)
def extract_keywords_from_text(text_content):
    """Mocks keyword extraction. Replace with spaCy/NLTK/etc."""
    if not text_content:
        return []

    # Simple logic: extract words longer than 5 chars, limit to 20 unique
    words = re.findall(r'\b[A-Za-z]{6,}\b', text_content.lower())
    # Mock tags: 'noun' for all, 'relevance' based on word length
    unique_keywords = sorted(list(set(words)))[:20] 

    keywords = []
    for keyword in unique_keywords:
        keywords.append({
            'keyword': keyword,
            'keyword_type': 'noun', 
            'frequency': words.count(keyword),
            'relevance_score': len(keyword) / 10.0  # Mock score
        })
    return keywords

# --- Main Extraction Logic ---
def run_extractor():
    session = Session()
    try:
        # Get all law IDs and full text from the OLD OpenParliament tables
        # Joining bills_bill and bills_billtext to get ID and content
        logging.info("Querying old bills_bill and bills_billtext tables...")
        
        # NOTE: This assumes your old Django-style tables are still named 'bills_bill' and 'bills_billtext'
        old_laws_query = text("""
            SELECT 
                b.id, 
                b.title, 
                t.text_html 
            FROM 
                bills_bill b
            JOIN 
                bills_billtext t ON b.current_version_id = t.id
            WHERE
                t.text_html IS NOT NULL AND t.text_html != ''
        """)
        
        results = session.execute(old_laws_query).fetchall()
        
        total_laws = len(results)
        logging.info(f"Found {total_laws} laws to process.")

        for index, row in enumerate(results):
            law_id = f"CA-{row[0]}"  # Prefix ID to make it universal (CA for Canada)
            title = row[1]
            full_text = row[2]
            
            logging.info(f"Processing ({index + 1}/{total_laws}): ID={law_id}, Title='{title[:40]}...'")

            # 1. Populate LawContent table
            law_content = session.query(LawContent).filter_by(id=law_id).first()
            if not law_content:
                law_content = LawContent(
                    id=law_id,
                    source_url=f"https://openparliament.ca/bills/{row[0]}",
                    jurisdiction='CANADA',
                    short_title=title,
                    full_text=full_text,
                    # We are only migrating text content for now
                )
                session.add(law_content)
                session.commit()
            
            # 2. Extract Keywords and Populate BillKeyword table
            keywords_data = extract_keywords_from_text(full_text)
            
            # Clear old keywords before adding new ones (for idempotency)
            session.query(BillKeyword).filter_by(law_id=law_id).delete()
            
            new_keywords = [
                BillKeyword(
                    law_id=law_id,
                    keyword=kw['keyword'],
                    keyword_type=kw['keyword_type'],
                    frequency=kw['frequency'],
                    relevance_score=kw['relevance_score']
                ) 
                for kw in keywords_data
            ]
            session.add_all(new_keywords)
            session.commit()
            
        logging.info("--- Extraction and Refactoring Complete! ---")

    except Exception as e:
        session.rollback()
        logging.error(f"An error occurred during extraction: {e}")
        
    finally:
        session.close()

if __name__ == '__main__':
    run_extractor()
