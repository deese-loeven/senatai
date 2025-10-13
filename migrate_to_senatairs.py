import sqlite3
import glob

def migrate_database(db_path):
    """Rename Users table to Senatairs and update foreign keys"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if Users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Users'")
        if cursor.fetchone():
            print(f"Migrating {db_path}...")
            
            # Rename table
            cursor.execute("ALTER TABLE Users RENAME TO Senatairs")
            
            # Update foreign key columns in related tables
            try:
                cursor.execute("ALTER TABLE Answers RENAME COLUMN user_id TO Senatair_id")
            except:
                print("  - No Answers table or already migrated")
                
            try:
                cursor.execute("ALTER TABLE Predictions RENAME COLUMN user_id TO Senatair_id") 
            except:
                print("  - No Predictions table or already migrated")
                
            try:
                cursor.execute("ALTER TABLE Audits RENAME COLUMN user_id TO Senatair_id")
            except:
                print("  - No Audits table or already migrated")
            
            conn.commit()
            print(f"✓ Successfully migrated {db_path}")
        else:
            print(f"✓ {db_path} already migrated or no Users table")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error migrating {db_path}: {e}")
        return False

# Migrate all databases
print("Starting database migration to Senatairs terminology...")
for db_file in glob.glob("*.db"):
    migrate_database(db_file)

print("Migration complete!")
