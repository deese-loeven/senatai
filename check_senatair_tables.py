# check_user_tables.py
import psycopg2

def check_user_tables():
    conn = psycopg2.connect(
        dbname="openparliament", 
        user="dan",
        password="senatai2025",
        host="localhost"
    )
    cur = conn.cursor()
    
    # Check all tables in the database
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    
    print("📋 ALL TABLES IN DATABASE:")
    tables = [row[0] for row in cur.fetchall()]
    for table in tables:
        print(f"   - {table}")
    
    # Check for user-related tables
    user_tables = [t for t in tables if 'user' in t.lower() or 'senatair' in t.lower()]
    if user_tables:
        print(f"\n🎯 USER-RELATED TABLES: {user_tables}")
        for table in user_tables:
            cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'")
            columns = [row[0] for row in cur.fetchall()]
            print(f"   {table}: {columns}")
    else:
        print("\n❌ NO USER TABLES FOUND")
    
    # Check for response/answer tables
    response_tables = [t for t in tables if 'response' in t.lower() or 'answer' in t.lower()]
    if response_tables:
        print(f"\n📝 RESPONSE TABLES: {response_tables}")
        for table in response_tables:
            cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'")
            columns = [row[0] for row in cur.fetchall()]
            print(f"   {table}: {columns}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_user_tables()
