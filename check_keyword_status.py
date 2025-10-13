# check_keyword_status.py
import psycopg2

def check_status():
    conn = psycopg2.connect(
        dbname="openparliament",
        user="dan",
        password="senatai2025",
        host="localhost"
    )
    cur = conn.cursor()
    
    # Count bills processed
    cur.execute("SELECT COUNT(DISTINCT bill_id) FROM bill_keywords")
    bill_count = cur.fetchone()[0]
    
    # Count total keywords
    cur.execute("SELECT COUNT(*) FROM bill_keywords")
    keyword_count = cur.fetchone()[0]
    
    # Show some sample keywords
    cur.execute("""
        SELECT bill_number, keyword, keyword_type, frequency 
        FROM bill_keywords 
        ORDER BY frequency DESC, relevance_score DESC 
        LIMIT 10
    """)
    
    print(f"📊 Keyword Database Status:")
    print(f"   Bills processed: {bill_count}")
    print(f"   Total keywords: {keyword_count}")
    print(f"   Average keywords per bill: {keyword_count/bill_count:.1f}" if bill_count > 0 else "0")
    
    print(f"\n🏆 Top 10 Keywords:")
    for i, row in enumerate(cur.fetchall(), 1):
        print(f"   {i}. {row[1]} ({row[2]}) - Bill {row[0]} (freq: {row[3]})")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_status()
