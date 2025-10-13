# check_schema.py
import psycopg2

conn = psycopg2.connect(
    dbname="openparliament",
    user="postgres",
    password="senatai2025", 
    host="localhost"
)
cur = conn.cursor()

# Check bills_billtext columns
cur.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'bills_billtext'
""")
print("bills_billtext columns:", [row[0] for row in cur.fetchall()])

# Check bills_bill columns  
cur.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'bills_bill'
""")
print("bills_bill columns:", [row[0] for row in cur.fetchall()])

cur.close()
conn.close()
