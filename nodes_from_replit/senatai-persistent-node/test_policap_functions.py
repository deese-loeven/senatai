import psycopg2
from datetime import date
import policap_rewards

try:
    conn = psycopg2.connect(
        dbname="openparliament",
        user="dan",
        password="senatai2025",
        host="localhost"
    )
    cursor = conn.cursor()
    
    print("Testing get_daily_stats...")
    stats = policap_rewards.get_daily_stats(cursor, 1, date.today())
    print(f"Stats: {stats}")
    
    print("Testing get_daily_stats_postgres...")
    stats_pg = policap_rewards.get_daily_stats_postgres(cursor, 1, date.today())
    print(f"PostgreSQL Stats: {stats_pg}")
    
    cursor.close()
    conn.close()
    print("✅ All policap functions work!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
