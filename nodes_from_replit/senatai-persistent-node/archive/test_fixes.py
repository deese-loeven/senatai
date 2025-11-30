#!/usr/bin/env python3
"""
Quick test script for the fixed routes
"""

import psycopg2
import os

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://localhost/openparliament')

def test_database_queries():
    """Test the problematic queries"""
    
    print("Testing database queries...")
    
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
        cursor = conn.cursor()
        
        # Test 1: Consensus forums query
        print("\n1. Testing consensus forums query...")
        cursor.execute('SELECT bill_id, bill_title, bill_summary, category, status FROM legislation LIMIT 5')
        bills = cursor.fetchall()
        print(f"   ✓ Got {len(bills)} bills")
        if bills:
            print(f"   ✓ First bill: {bills[0]['bill_id']} - {bills[0]['status']}")
        
        # Test 2: Trending/complaints count
        print("\n2. Testing complaints count query...")
        cursor.execute('SELECT COUNT(*) as count FROM complaints')
        result = cursor.fetchone()
        count = result['count'] if result else 0
        print(f"   ✓ Total complaints: {count}")
        
        # Test 3: Username uniqueness check
        print("\n3. Testing username lookup...")
        cursor.execute('SELECT username FROM senatairs LIMIT 1')
        user = cursor.fetchone()
        if user:
            print(f"   ✓ Found existing user: {user['username']}")
        
        conn.close()
        print("\n✅ All database queries working!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    import psycopg2.extras
    test_database_queries()
