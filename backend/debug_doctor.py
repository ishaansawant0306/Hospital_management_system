from main import app
from models.models import Doctor, User, Department
from sqlalchemy import or_

def debug_doctor():
    with app.app_context():
        print("--- Debugging Doctor Visibility ---")
        
        # 1. Search for the specific doctor
        search_name = "Ishaan"
        doctors = Doctor.query.join(User).filter(User.username.ilike(f'%{search_name}%')).all()
        
        if not doctors:
            print(f"No doctor found with name matching '{search_name}'")
        
        for doc in doctors:
            print(f"Doctor ID: {doc.id}")
            print(f"User ID: {doc.user_id}")
            print(f"Username: {doc.user.username}")
            print(f"Specialization: '{doc.specialization}'")
            print(f"Is Blacklisted: {doc.user.is_blacklisted}")
            print(f"Department Mapping Check:")
            
            # Check against mapping logic
            dept_name = 'cardiology'
            department_mapping = {
                'cardiology': ['cardiology', 'cardiologist'],
                'oncology': ['oncology', 'oncologist'],
                'general': ['general', 'internal medicine', 'general medicine']
            }
            search_terms = department_mapping.get(dept_name, [])
            print(f"  Target Dept: {dept_name}")
            print(f"  Search Terms: {search_terms}")
            
            match = False
            for term in search_terms:
                if term.lower() in doc.specialization.lower():
                    match = True
                    print(f"  MATCH FOUND with term: '{term}'")
                    break
            
            if not match:
                print("  NO MATCH with cardiology terms.")

        # 2. List all doctors to see what's available
        print("\n--- All Doctors ---")
        all_docs = Doctor.query.all()
        for doc in all_docs:
            username = doc.user.username if doc.user else "NO USER"
            print(f"Doc: {username}, Spec: {doc.specialization}")

if __name__ == "__main__":
    debug_doctor()
