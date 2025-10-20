import psycopg2
import os

try:
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        print("❌ DATABASE_URL not set")
        exit(1)
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM legislation;")
    count = cursor.fetchone()[0]
    print(f"✅ Database connected successfully! Found {count} bills in legislation table.")
    
    cursor.execute("SELECT COUNT(*) FROM senatairs;")
    user_count = cursor.fetchone()[0]
    print(f"✅ Found {user_count} senatairs in database.")
    
    conn.close()
except Exception as e:
    print(f"❌ Database connection failed: {e}")
