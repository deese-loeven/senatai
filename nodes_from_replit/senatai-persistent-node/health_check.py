#!/usr/bin/env python3
"""
Quick Senatai Health Check
Tests core functionality before inviting testers
"""
import requests
import time
import sys

def test_server_health():
    base_url = "http://localhost:5000"
    
    print("🧪 SENATAI SERVER HEALTH CHECK")
    print("=" * 40)
    
    # Test 1: Server responsiveness
    print("1. Testing server connectivity...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("   ✅ Server is responding")
        else:
            print(f"   ❌ Server returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot connect to server: {e}")
        return False
    
    # Test 2: Core pages load
    print("2. Testing core page loading...")
    pages_to_test = ["/speak", "/profile", "/trending"]
    
    for page in pages_to_test:
        try:
            response = requests.get(f"{base_url}{page}", timeout=10)
            if response.status_code == 200:
                print(f"   ✅ {page} loads successfully")
            else:
                print(f"   ⚠️  {page} returned {response.status_code}")
        except Exception as e:
            print(f"   ❌ {page} failed: {e}")
    
    # Test 3: Icebreaker functionality
    print("3. Testing icebreaker search...")
    test_inputs = [
        "climate change",
        "healthcare",
        "education"
    ]
    
    for test_input in test_inputs:
        try:
            response = requests.post(
                f"{base_url}/search_bills",
                data={"user_input": test_input},
                timeout=15
            )
            if response.status_code == 200:
                print(f"   ✅ '{test_input}' search completed")
            else:
                print(f"   ⚠️  '{test_input}' search issue: {response.status_code}")
        except Exception as e:
            print(f"   ❌ '{test_input}' search failed: {e}")
    
    print("\n🎯 READINESS ASSESSMENT:")
    print("If all ✅ marks above, server is ready for testers!")
    print("If ⚠️ marks, consider fixing before inviting users")
    print("If ❌ marks, needs immediate attention")
    
    return True

if __name__ == "__main__":
    # Give server time to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    test_server_health()
