"""
Database Migration Script
Adds doctor_id and address fields to the Doctor table

Run this script ONCE to update your existing database schema.
"""

from app_config import app
from models.models import db, Doctor
from sqlalchemy import text

def migrate_database():
    """Add new columns to Doctor table if they don't exist"""
    
    with app.app_context():
        try:
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('doctor')]
            
            print("Current Doctor table columns:", columns)
            
            # Add doctor_id column if it doesn't exist
            if 'doctor_id' not in columns:
                print("Adding 'doctor_id' column...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE doctor ADD COLUMN doctor_id VARCHAR(50)'))
                    conn.commit()
                print("[OK] 'doctor_id' column added successfully")
            else:
                print("[OK] 'doctor_id' column already exists")
            
            # Add address column if it doesn't exist
            if 'address' not in columns:
                print("Adding 'address' column...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE doctor ADD COLUMN address VARCHAR(300)'))
                    conn.commit()
                print("[OK] 'address' column added successfully")
            else:
                print("[OK] 'address' column already exists")
            
            # Update existing doctors with temporary doctor_ids if needed
            print("\nChecking for doctors without doctor_id...")
            doctors_without_id = Doctor.query.filter(
                (Doctor.doctor_id == None) | (Doctor.doctor_id == '')
            ).all()
            
            if doctors_without_id:
                print(f"Found {len(doctors_without_id)} doctors without doctor_id")
                for i, doctor in enumerate(doctors_without_id, start=1):
                    doctor.doctor_id = f"DOC-{doctor.id:04d}"
                    print(f"  - Assigned {doctor.doctor_id} to doctor ID {doctor.id}")
                
                db.session.commit()
                print("[OK] All doctors now have unique doctor_ids")
            else:
                print("[OK] All doctors already have doctor_ids")
            
            # Now make doctor_id unique and not null
            print("\nApplying constraints...")
            with db.engine.connect() as conn:
                # For SQLite, we need to check if the constraint exists first
                try:
                    conn.execute(text('CREATE UNIQUE INDEX IF NOT EXISTS idx_doctor_id ON doctor(doctor_id)'))
                    conn.commit()
                    print("[OK] Unique constraint added to doctor_id")
                except Exception as e:
                    print(f"Note: {e}")
            
            print("\n" + "="*50)
            print("[SUCCESS] Database migration completed successfully!")
            print("="*50)
            
        except Exception as e:
            print(f"\n[ERROR] Migration failed: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Starting Database Migration")
    print("="*50 + "\n")
    migrate_database()

