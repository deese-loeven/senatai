#!/bin/bash

echo "=== STEP 1: Clear Legislation Table ==="
psql -d openparliament -c "TRUNCATE TABLE legislation RESTART IDENTITY;"

echo "=== STEP 2: Insert Basic Bill Data ==="
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

echo "=== STEP 3: Verify Initial Insert ==="
psql -d openparliament -c "SELECT COUNT(*) as bills_loaded FROM legislation;"

echo "=== STEP 4: Update with Summaries ==="
psql -d openparliament -c "
UPDATE legislation 
SET bill_summary = bt.summary_en
FROM bills_bill b 
JOIN bills_billtext bt ON b.id = bt.bill_id
WHERE legislation.bill_id = b.number;"

echo "=== STEP 5: Final Verification ==="
psql -d openparliament -c "SELECT COUNT(*) as total_bills FROM legislation;"
psql -d openparliament -c "SELECT COUNT(*) as bills_with_summaries FROM legislation WHERE bill_summary != 'No summary available';"
psql -d openparliament -c "SELECT bill_id, bill_title, LEFT(bill_summary, 50) as summary_preview FROM legislation LIMIT 5;"

echo "🎉 Legislation table rebuilt successfully!"
