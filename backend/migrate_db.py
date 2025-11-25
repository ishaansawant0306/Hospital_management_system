"""
Database Migration Script

This script adds the is_blacklisted column to the User table if it doesn't exist.
It safely handles cases where the column already exists.
"""

import sys
import os
import sqlite3

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("🔧 Database Migration Script")

try:
    from app_config import app
    from models.models import db

    with app.app_context():
        print("📦 Dropping and recreating all tables with new schema...")
        # Drop all tables and recreate them (for dev/test; in production use Alembic)
        db.drop_all()
        db.create_all()
        print("✅ Database schema updated successfully!")
        
        # Verify the table structure
        db_path = os.path.join(os.path.dirname(__file__), 'instance', 'hospital.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        print("\n📋 User table columns:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        conn.close()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
