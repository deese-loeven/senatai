import sqlite3
import glob

def update_database_tables(db_path):
    """Update database tables from users to Senatairs"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if cursor.fetchone():
            print(f"Updating users table to Senatairs in {db_path}...")
            
            # Rename table
            cursor.execute("ALTER TABLE users RENAME TO Senatairs")
            
            # Update foreign key references in other tables if they exist
            try:
                cursor.execute("ALTER TABLE Answers RENAME COLUMN user_id TO Senatair_id")
            except:
                pass
                
            try:
                cursor.execute("ALTER TABLE Predictions RENAME COLUMN user_id TO Senatair_id")
            except:
                pass
                
            try:
                cursor.execute("ALTER TABLE Audits RENAME COLUMN user_id TO Senatair_id")
            except:
                pass
        
        conn.commit()
        conn.close()
        print(f"✓ Updated {db_path}")
        return True
        
    except Exception as e:
        print(f"✗ Error updating {db_path}: {e}")
        return False

# Update all databases
for db_file in glob.glob("*.db"):
    update_database_tables(db_file)

print("Database table updates complete!")
