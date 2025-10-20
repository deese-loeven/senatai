-- Initialize additional tables needed for Senatai in PostgreSQL
-- Run this on your Ubuntu laptop: psql -U dan -d openparliament -f init_postgres_tables.sql

-- Daily vote tracking for Policap diminishing returns
CREATE TABLE IF NOT EXISTS daily_vote_count (
    id SERIAL PRIMARY KEY,
    senatair_id INTEGER NOT NULL REFERENCES senatairs(id),
    vote_date DATE NOT NULL,
    vote_count INTEGER DEFAULT 0,
    UNIQUE(senatair_id, vote_date)
);

-- Policap transaction history
CREATE TABLE IF NOT EXISTS policap_transactions (
    id SERIAL PRIMARY KEY,
    senatair_id INTEGER NOT NULL REFERENCES senatairs(id),
    amount DECIMAL(10,2) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    description TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vote predictions (for future AI modules)
CREATE TABLE IF NOT EXISTS vote_predictions (
    id SERIAL PRIMARY KEY,
    senatair_id INTEGER NOT NULL REFERENCES senatairs(id),
    bill_number VARCHAR(20) NOT NULL,
    predicted_vote VARCHAR(10) NOT NULL,
    confidence DECIMAL(5,2),
    module_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Policap spending on bills (for auditing predictions)
CREATE TABLE IF NOT EXISTS policap_spending (
    id SERIAL PRIMARY KEY,
    senatair_id INTEGER NOT NULL REFERENCES senatairs(id),
    bill_number VARCHAR(20) NOT NULL,
    policap_spent DECIMAL(10,2) NOT NULL,
    spending_type VARCHAR(20) NOT NULL,
    position_change_reason TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Question generator modules
CREATE TABLE IF NOT EXISTS question_modules (
    id SERIAL PRIMARY KEY,
    module_name VARCHAR(100) UNIQUE NOT NULL,
    module_description TEXT,
    version VARCHAR(20),
    rating DECIMAL(3,1) DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vote predictor modules
CREATE TABLE IF NOT EXISTS predictor_modules (
    id SERIAL PRIMARY KEY,
    module_name VARCHAR(100) UNIQUE NOT NULL,
    module_description TEXT,
    version VARCHAR(20),
    rating DECIMAL(3,1) DEFAULT 0.0,
    accuracy_history TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add accepted_terms and accepted_coop_agreement to senatairs if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='senatairs' AND column_name='accepted_terms') THEN
        ALTER TABLE senatairs ADD COLUMN accepted_terms BOOLEAN DEFAULT FALSE;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='senatairs' AND column_name='accepted_coop_agreement') THEN
        ALTER TABLE senatairs ADD COLUMN accepted_coop_agreement BOOLEAN DEFAULT FALSE;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='senatairs' AND column_name='password_hash') THEN
        ALTER TABLE senatairs ADD COLUMN password_hash VARCHAR(255);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='senatairs' AND column_name='is_admin') THEN
        ALTER TABLE senatairs ADD COLUMN is_admin BOOLEAN DEFAULT FALSE;
    END IF;
END $$;

-- Questions and responses tables for sophisticated question system
CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    bill_id VARCHAR(20) NOT NULL,
    question_type VARCHAR(50) NOT NULL,
    question_text TEXT NOT NULL,
    question_options TEXT,
    module_name VARCHAR(100),
    clause_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS question_responses (
    id SERIAL PRIMARY KEY,
    senatair_id INTEGER NOT NULL REFERENCES senatairs(id),
    question_id INTEGER NOT NULL REFERENCES questions(id),
    bill_id VARCHAR(20) NOT NULL,
    response_value TEXT NOT NULL,
    response_numeric DECIMAL(10,2),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Complaints and topic interest tables for "Post and Ghost" feature
CREATE TABLE IF NOT EXISTS complaints (
    id SERIAL PRIMARY KEY,
    complaint_text TEXT NOT NULL,
    guest_session_id VARCHAR(100),
    detected_topics TEXT,
    matched_bills TEXT,
    matched_categories TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS topic_interest (
    id SERIAL PRIMARY KEY,
    topic_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    interest_count INTEGER DEFAULT 1,
    last_mentioned TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Demographic data for rich dataset creation (premium client value)
CREATE TABLE IF NOT EXISTS demographic_data (
    id SERIAL PRIMARY KEY,
    senatair_id INTEGER REFERENCES senatairs(id),
    guest_session_id VARCHAR(100),
    age_range VARCHAR(20),
    gender VARCHAR(50),
    region VARCHAR(100),
    work_experience TEXT,
    expertise_areas TEXT,
    education_level VARCHAR(50),
    provided_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Daily question and vote tracking for Policap rewards with diminishing returns
CREATE TABLE IF NOT EXISTS daily_question_count (
    id SERIAL PRIMARY KEY,
    senatair_id INTEGER REFERENCES senatairs(id),
    activity_date DATE NOT NULL,
    question_count INTEGER DEFAULT 0,
    vote_count INTEGER DEFAULT 0,
    UNIQUE(senatair_id, activity_date)
);

-- Add badge tracking columns to senatairs table (run separately if table already exists)
-- ALTER TABLE senatairs ADD COLUMN IF NOT EXISTS lifetime_policap_earned DECIMAL(10,2) DEFAULT 0.00;
-- ALTER TABLE senatairs ADD COLUMN IF NOT EXISTS total_audits_made INTEGER DEFAULT 0;

-- Insert sample modules
INSERT INTO question_modules (module_name, module_description, version, rating) 
VALUES ('Sophisticated Question Generator', 'Generates emotional, values, fairness, and principle-based questions', '1.0', 4.8)
ON CONFLICT (module_name) DO NOTHING;

INSERT INTO question_modules (module_name, module_description, version, rating) 
VALUES ('Basic Binary', 'Simple Yes/No question generator based on bill summaries', '1.0', 4.2)
ON CONFLICT (module_name) DO NOTHING;

INSERT INTO predictor_modules (module_name, module_description, version, rating, accuracy_history) 
VALUES ('Template Predictor', 'Template for future AI-powered vote prediction', '1.0', 3.5, 'No historical data yet')
ON CONFLICT (module_name) DO NOTHING;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_daily_vote_senatair_date ON daily_vote_count(senatair_id, vote_date);
CREATE INDEX IF NOT EXISTS idx_policap_trans_senatair ON policap_transactions(senatair_id);
CREATE INDEX IF NOT EXISTS idx_questions_bill_id ON questions(bill_id);
CREATE INDEX IF NOT EXISTS idx_question_responses_senatair ON question_responses(senatair_id);
CREATE INDEX IF NOT EXISTS idx_question_responses_question ON question_responses(question_id);

-- Create indexes for existing user tables (if they exist)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='senatair_responses') THEN
        EXECUTE 'CREATE INDEX IF NOT EXISTS idx_senatair_responses_senatair ON senatair_responses(senatair_id)';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='bills_bill') THEN
        EXECUTE 'CREATE INDEX IF NOT EXISTS idx_bills_number ON bills_bill(number)';
    END IF;
END $$;

-- Success message
DO $$
DECLARE
    bill_count INTEGER;
BEGIN
    RAISE NOTICE '✅ Senatai tables created successfully!';
    
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='bills_bill') THEN
        SELECT COUNT(*) INTO bill_count FROM bills_bill;
        RAISE NOTICE 'Your database now has % bills ready for voting.', bill_count;
    ELSE
        RAISE NOTICE 'Note: bills_bill table not found. You may need to import your legislation data.';
    END IF;
END $$;
