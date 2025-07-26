CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    theme TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER,
    user_id TEXT,
    answer TEXT,
    policaps_earned REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (question_id) REFERENCES questions (id)
);

CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    bill_text TEXT,
    prediction TEXT,
    confidence REAL,
    explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Add to schema.sql
CREATE TABLE IF NOT EXISTS laws (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_text TEXT NOT NULL,
    jurisdiction TEXT,  -- national/provincial/local
    source_url TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Link questions to laws
ALTER TABLE questions ADD COLUMN law_id INTEGER REFERENCES laws(id);

-- Track policap transactions
CREATE TABLE IF NOT EXISTS policaps (
    user_id TEXT NOT NULL,
    amount REAL NOT NULL,
    action TEXT,  -- "earned", "spent", "donated"
    linked_to INTEGER,  -- answer_id or prediction_id
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
