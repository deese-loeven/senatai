-- database_schema_template.sql
-- SENATAI Database Schema Template
-- Use this to set up your own PostgreSQL database for SENATAI

-- Create database (run this separately)
-- CREATE DATABASE openparliament;

-- Connect to your database and run these:

-- Bills table (from OpenParliament)
CREATE TABLE IF NOT EXISTS bills_bill (
    id SERIAL PRIMARY KEY,
    number VARCHAR(20) UNIQUE NOT NULL,
    short_title_en TEXT,
    summary_en TEXT,
    introduced DATE,
    sponsor_politician_id INTEGER,
    law BOOLEAN DEFAULT FALSE,
    status_code VARCHAR(50)
);

-- Bill text table
CREATE TABLE IF NOT EXISTS bills_billtext (
    id SERIAL PRIMARY KEY,
    bill_id INTEGER REFERENCES bills_bill(id),
    text_en TEXT,
    summary_en TEXT
);

-- Keywords table (populated by batch_keyword_extractor)
CREATE TABLE IF NOT EXISTS bill_keywords (
    id SERIAL PRIMARY KEY,
    bill_id INTEGER,
    bill_number VARCHAR(20),
    keyword VARCHAR(100),
    keyword_type VARCHAR(50),
    frequency INTEGER,
    relevance_score FLOAT,
    UNIQUE(bill_id, keyword, keyword_type)
);

-- User authentication tables
CREATE TABLE IF NOT EXISTS senatairs (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP,
    policaps FLOAT DEFAULT 25.0,
    daily_answer_count INTEGER DEFAULT 0,
    last_reset DATE DEFAULT CURRENT_DATE
);

-- Session tracking
CREATE TABLE IF NOT EXISTS senatair_sessions (
    id SERIAL PRIMARY KEY,
    senatair_id INTEGER REFERENCES senatairs(id),
    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_end TIMESTAMP,
    questions_answered INTEGER DEFAULT 0,
    policaps_earned FLOAT DEFAULT 0.0
);

-- Response storage
CREATE TABLE IF NOT EXISTS senatair_responses (
    id SERIAL PRIMARY KEY,
    senatair_id INTEGER REFERENCES senatairs(id),
    session_id INTEGER REFERENCES senatair_sessions(id),
    question_text TEXT,
    answer_text TEXT,
    bill_number VARCHAR(20),
    question_type VARCHAR(50),
    matched_keywords TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_bill_keywords_keyword ON bill_keywords(keyword);
CREATE INDEX IF NOT EXISTS idx_bill_keywords_bill_number ON bill_keywords(bill_number);
CREATE INDEX IF NOT EXISTS idx_bills_bill_number ON bills_bill(number);
CREATE INDEX IF NOT EXISTS idx_senatairs_username ON senatairs(username);
