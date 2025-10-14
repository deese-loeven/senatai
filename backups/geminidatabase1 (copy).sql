-- SQLite Database Schema

-- Bills Table
CREATE TABLE Bills (
    bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_number VARCHAR(255),
    bill_title TEXT,
    bill_link TEXT,
    source VARCHAR(255),
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Questions Table
CREATE TABLE Questions (
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_id INTEGER,
    question_text TEXT,
    question_maker VARCHAR(255),
    FOREIGN KEY (bill_id) REFERENCES Bills(bill_id)
);

-- Users Table
CREATE TABLE Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(255) UNIQUE,
    email VARCHAR(255) UNIQUE,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Answers Table
CREATE TABLE Answers (
    answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER,
    user_id INTEGER,
    answer_text TEXT,
    answer_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    token VARCHAR(255) UNIQUE,
    FOREIGN KEY (question_id) REFERENCES Questions(question_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- Predictions Table
CREATE TABLE Predictions (
    prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_id INTEGER,
    user_id INTEGER,
    predictor_name VARCHAR(255),
    predicted_vote VARCHAR(255),
    prediction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bill_id) REFERENCES Bills(bill_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- Audits Table
CREATE TABLE Audits (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    prediction_id INTEGER,
    user_id INTEGER,
    audit_action VARCHAR(255),
    audit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    token VARCHAR(255),
    FOREIGN KEY (prediction_id) REFERENCES Predictions(prediction_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (token) REFERENCES Answers(token)
);

--Example insert statements
-- Insert Example Bill
INSERT INTO Bills (bill_number, bill_title, bill_link, source) VALUES ('Bill 123', 'Example Bill Title', 'http://example.com/bill123', 'main_scraper2');

-- Insert Example Question
INSERT INTO Questions (bill_id, question_text, question_maker) VALUES (1, 'Does this bill affect...', 'Question Generator A');

-- Insert Example User
INSERT INTO Users (username, email) VALUES ('testuser', 'test@example.com');

-- Insert Example Answer
INSERT INTO Answers (question_id, user_id, answer_text, token) VALUES (1, 1, 'Yes, it does.', 'unique_token_1');

-- Insert example prediction
INSERT INTO Predictions (bill_id, user_id, predictor_name, predicted_vote) VALUES (1,1, 'Predictor A', 'Yes');

--Insert example audit
INSERT INTO Audits (prediction_id, user_id, audit_action, token) VALUES (1, 1, 'affirmed', 'unique_token_1');
