"""
Create Admin User Script

This script initializes the database and creates a default admin user for the Hospital Management System.
It should be run once during the initial setup of the application.

Features:
    - Adds the parent directory to the Python path for module imports
    - Creates all database tables
    - Checks if an admin user already exists
    - Creates a default admin user if one doesn't exist
"""

import sys
import os

# Add the parent directory to the Python path to allow imports from the backend folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("🧠 Debugging create_admin.py")
print("🚀 Script execution started")

try:
    # Import necessary modules and dependencies
    print("🔍 Importing modules...")
    from models.models import db, User
    from app_config import app  # Import `app` from the new configuration file
    from werkzeug.security import generate_password_hash

    # Enter the Flask application context to interact with the database
    print("🔧 Entering app context...")
    with app.app_context():
        # Create all database tables based on defined models
        print("📦 Creating database tables...")
        db.create_all()
        # Add is_blacklisted column if missing
        print("🛡️ Checking for is_blacklisted column...")
        import sqlite3
        db_path = os.path.join("backend", "instance", "hospital.db")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(user);")
        cols = [row[1] for row in cur.fetchall()]
        if "is_blacklisted" not in cols:
            cur.execute("ALTER TABLE user ADD COLUMN is_blacklisted INTEGER DEFAULT 0;")
            conn.commit()
            print("✅ Column is_blacklisted added.")
        else:
            print("ℹ️ Column is_blacklisted already exists.")
        conn.close()

        # Check if an admin user already exists in the database
        print("🔍 Checking for existing admin user...")
        existing_admin = User.query.filter_by(role='Admin').first()
        
        # If no admin exists, create a new one with default credentials
        if not existing_admin:
            print("🛠️ Creating new admin user...")
            user = User(
                username='admin',
                email='admin@hospital.com',
                password=generate_password_hash('admin123'),
                role='Admin'
            )
            db.session.add(user)
            db.session.commit()
            print('✅ Admin user created.')
        else:
            # Admin user already exists, so skip creation
            print('⚠️ Admin already exists.')
 
except Exception as e:
    # Catch and display any errors that occur during execution
    print("❌ Error occurred:", e)
    import traceback
    traceback.print_exc()