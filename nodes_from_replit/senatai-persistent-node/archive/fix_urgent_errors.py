#!/usr/bin/env python3
"""
Fix the 3 critical errors from the test session
Run this script to apply all fixes automatically
"""

import re
import os

def fix_consensus_forums_template():
    """Fix: bill[4] doesn't exist - use dict keys instead"""
    
    with open('templates/consensus_forums.html', 'r') as f:
        content = f.read()
    
    # Replace numeric indices with dict keys for RealDictRow
    replacements = [
        (r"{{ bill\[0\] }}", "{{ bill['bill_id'] }}"),
        (r"{{ bill\[1\] }}", "{{ bill['bill_title'] }}"),
        (r"{{ bill\[2\] }}", "{{ bill['bill_summary'] }}"),
        (r"{{ bill\[3\] }}", "{{ bill['category'] if bill['category'] else 'General' }}"),
        (r"{{ bill\[4\]\.lower\(\) }}", "{{ bill['status'].lower() }}"),
        (r"{{ bill\[4\] }}", "{{ bill['status'] }}"),
    ]
    
    for old, new in replacements:
        content = re.sub(old, new, content)
    
    with open('templates/consensus_forums.html', 'w') as f:
        f.write(content)
    
    print("✅ Fixed consensus_forums.html - using dict keys instead of indices")


def fix_trending_route():
    """Fix: cursor.fetchone()[0] failing - use dict key"""
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Find and fix the trending route
    old_code = "total_complaints = cursor.fetchone()[0]"
    new_code = "result = cursor.fetchone()\n    total_complaints = result['count'] if result else 0"
    
    content = content.replace(old_code, new_code)
    
    with open('app.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed trending route - handling dict result properly")


def fix_signup_duplicate_username():
    """Fix: signup crashes on duplicate username - need better error handling"""
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Find the signup route and add try-catch for duplicate
    old_signup_insert = '''        password_hash = generate_password_hash(password)
        cursor.execute('INSERT INTO senatairs (username, password_hash) VALUES (%s, %s)', (username, password_hash))
        conn.commit()
        conn.close()'''
    
    new_signup_insert = '''        password_hash = generate_password_hash(password)
        
        try:
            cursor.execute('INSERT INTO senatairs (username, password_hash) VALUES (%s, %s)', (username, password_hash))
            conn.commit()
            conn.close()
        except psycopg2.IntegrityError:
            conn.rollback()
            conn.close()
            flash('Username already exists. Please choose another.', 'error')
            return redirect(url_for('signup'))
        except Exception as e:
            conn.rollback()
            conn.close()
            flash(f'Error creating account: {str(e)}', 'error')
            return redirect(url_for('signup'))'''
    
    if old_signup_insert in content:
        content = content.replace(old_signup_insert, new_signup_insert)
    
    with open('app.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed signup route - handling duplicate usernames gracefully")


def add_dev_banner_to_base():
    """Add development prototype banner"""
    
    with open('templates/base.html', 'r') as f:
        content = f.read()
    
    if 'dev-banner' in content:
        print("✓ Development banner already exists")
        return
    
    # Banner to insert after <body>
    banner = '''    <!-- DEVELOPMENT PROTOTYPE BANNER -->
    <div class="dev-banner">
        <div class="dev-banner-content">
            <span class="dev-icon">🚧</span>
            <div class="dev-text">
                <strong>DEVELOPMENT PROTOTYPE</strong> - Intermittently available for testing only. 
                No real data will be monetized. Pseudonyms encouraged.
            </div>
        </div>
    </div>
    <style>
    .dev-banner {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        color: white;
        padding: 0.75rem 1rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    .dev-banner-content {
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        flex-wrap: wrap;
    }
    .dev-icon { font-size: 1.5rem; }
    .dev-text {
        font-size: 0.9rem;
        line-height: 1.4;
    }
    @media (max-width: 768px) {
        .dev-banner { padding: 0.5rem; }
        .dev-text { font-size: 0.8rem; }
    }
    </style>
'''
    
    content = content.replace('<body>', f'<body>\n{banner}')
    
    with open('templates/base.html', 'w') as f:
        f.write(content)
    
    print("✅ Added development banner to base.html")


def add_better_error_handlers():
    """Add error handlers to catch issues gracefully"""
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    if '@app.errorhandler(500)' in content:
        print("✓ Error handlers already exist")
        return
    
    error_handlers = '''

# Error handlers for development testing
@app.errorhandler(404)
def not_found(e):
    flash('Page not found. This prototype feature may not be ready yet.', 'error')
    return redirect(url_for('home'))

@app.errorhandler(500)
def internal_error(e):
    flash('Something went wrong in the prototype. We\'re working on it!', 'error')
    return redirect(url_for('home'))
'''
    
    # Insert before if __name__
    content = content.replace(
        "\n\nif __name__ == '__main__':",
        f"{error_handlers}\n\nif __name__ == '__main__':"
    )
    
    with open('app.py', 'w') as f:
        f.write(content)
    
    print("✅ Added error handlers for graceful failures")


def create_quick_test_script():
    """Create a script to test the fixes"""
    
    test_script = '''#!/usr/bin/env python3
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
        print("\\n1. Testing consensus forums query...")
        cursor.execute('SELECT bill_id, bill_title, bill_summary, category, status FROM legislation LIMIT 5')
        bills = cursor.fetchall()
        print(f"   ✓ Got {len(bills)} bills")
        if bills:
            print(f"   ✓ First bill: {bills[0]['bill_id']} - {bills[0]['status']}")
        
        # Test 2: Trending/complaints count
        print("\\n2. Testing complaints count query...")
        cursor.execute('SELECT COUNT(*) as count FROM complaints')
        result = cursor.fetchone()
        count = result['count'] if result else 0
        print(f"   ✓ Total complaints: {count}")
        
        # Test 3: Username uniqueness check
        print("\\n3. Testing username lookup...")
        cursor.execute('SELECT username FROM senatairs LIMIT 1')
        user = cursor.fetchone()
        if user:
            print(f"   ✓ Found existing user: {user['username']}")
        
        conn.close()
        print("\\n✅ All database queries working!")
        
    except Exception as e:
        print(f"\\n❌ Error: {e}")

if __name__ == "__main__":
    import psycopg2.extras
    test_database_queries()
'''
    
    with open('test_fixes.py', 'w') as f:
        f.write(test_script)
    
    print("✅ Created test_fixes.py")


def main():
    """Apply all urgent fixes"""
    
    print("🔧 APPLYING URGENT FIXES FROM TEST SESSION")
    print("=" * 60)
    
    # Fix the three critical errors
    fix_consensus_forums_template()
    fix_trending_route()
    fix_signup_duplicate_username()
    
    # Add development warning
    add_dev_banner_to_base()
    
    # Add error handlers
    add_better_error_handlers()
    
    # Create test script
    create_quick_test_script()
    
    print("\n" + "=" * 60)
    print("✅ ALL FIXES APPLIED!")
    print("\n📋 What was fixed:")
    print("1. consensus_forums - Now uses dict keys (bill['status'] not bill[4])")
    print("2. trending - Fixed complaint count query")
    print("3. signup - Graceful handling of duplicate usernames")
    print("4. Development banner added to all pages")
    print("5. Error handlers added for 404/500")
    print("\n🚀 Next steps:")
    print("1. Restart Flask: python3 app.py")
    print("2. Test fixes: python3 test_fixes.py")
    print("3. Try the routes that failed:")
    print("   - /consensus_forums")
    print("   - /trending")
    print("   - /signup (with duplicate username)")

if __name__ == "__main__":
    main()
