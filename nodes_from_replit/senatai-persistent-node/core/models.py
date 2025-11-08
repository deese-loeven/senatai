# ~/senatai/nodes_from_replit/senatai-persistent-node/core/models.py
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import declarative_base, sessionmaker

# Define a base class for models
Base = declarative_base()

# 1. Generic Law Content Table (Replaces bills_bill & bills_billtext)
class LawContent(Base):
    __tablename__ = 'law_content'
    # Use a string ID to accommodate various sources (e.g., 'CA-Bill-123', 'US-HR-456')
    id = Column(String(100), primary_key=True) 
    source_url = Column(Text)
    jurisdiction = Column(String(50), nullable=False) # e.g., 'CANADA', 'ONTARIO', 'USA'
    short_title = Column(String(500))
    summary_text = Column(Text)
    full_text = Column(Text)
    date_enacted = Column(DateTime)
    
    def __repr__(self):
        return f"<LawContent(id='{self.id}', title='{self.short_title[:30]}...')>"

# 2. Generic Keyword Table (Replaces bill_keywords)
class BillKeyword(Base):
    __tablename__ = 'bill_keywords'
    # Composite primary key for unique keyword per law
    __table_args__ = (
        PrimaryKeyConstraint('law_id', 'keyword', 'keyword_type', name='bill_keyword_pk'),
    )
    law_id = Column(String(100), ForeignKey('law_content.id'), nullable=False)
    keyword = Column(String(100), nullable=False)
    keyword_type = Column(String(50), nullable=False) # 'noun', 'entity_law', 'adjective'
    frequency = Column(Integer, default=1)
    relevance_score = Column(Float, default=0.0)
    
    def __repr__(self):
        return f"<BillKeyword(law_id='{self.law_id}', keyword='{self.keyword}', type='{self.keyword_type}')>"
