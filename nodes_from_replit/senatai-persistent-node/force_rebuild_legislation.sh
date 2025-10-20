#!/bin/bash

echo "=== STEP 1: Drop and Recreate Legislation Table ==="
psql -d openparliament -c "DROP TABLE IF EXISTS legislation CASCADE;"

psql -d openparliament -c "
CREATE TABLE legislation (
    id SERIAL PRIMARY KEY,
    bill_id VARCHAR(50) UNIQUE NOT NULL,
    bill_title TEXT NOT NULL,
    bill_summary TEXT NOT NULL,
    full_text TEXT,
    status VARCHAR(50) NOT NULL,
    category VARCHAR(100),
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);"

echo "=== STEP 2: Insert All Bills ==="
psql -d openparliament -c "
INSERT INTO legislation (bill_id, bill_title, bill_summary, status, category, source_url)
SELECT 
    number as bill_id,
    COALESCE(short_title_en, name_en, 'Untitled Bill') as bill_title,
    'No summary available' as bill_summary,
    COALESCE(status_code, 'Unknown') as status,
    'Canadian Law' as category,
    CONCAT('https://openparliament.ca/bills/', number, '/') as source_url
FROM bills_bill 
WHERE number IS NOT NULL;"

echo "=== STEP 3: Verify Insert ==="
psql -d openparliament -c "SELECT COUNT(*) as bills_inserted FROM legislation;"

echo "=== STEP 4: Update Summaries ==="
psql -d openparliament -c "
UPDATE legislation 
SET bill_summary = COALESCE(bt.summary_en, 'No summary available')
FROM bills_bill b 
LEFT JOIN bills_billtext bt ON b.id = bt.bill_id
WHERE legislation.bill_id = b.number;"

echo "=== STEP 5: Final Check ==="
psql -d openparliament -c "SELECT COUNT(*) as total_bills FROM legislation;"
psql -d openparliament -c "SELECT COUNT(*) as bills_with_real_summaries FROM legislation WHERE bill_summary != 'No summary available';"
psql -d openparliament -c "SELECT bill_id, bill_title FROM legislation LIMIT 5;"

echo "🎉 Legislation table rebuilt!"
