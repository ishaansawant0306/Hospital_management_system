
from app_config import app
from models.models import Doctor, User

with app.app_context():
    query_str = "DOC-2345"
    print(f"Searching for '{query_str}'...")
    
    try:
        doctors = Doctor.query.filter(
            (Doctor.specialization.ilike(f'%{query_str}%')) |
            (Doctor.user.has(User.username.ilike(f'%{query_str}%'))) |
            (Doctor.doctor_id.ilike(f'%{query_str}%'))
        ).all()
        
        print(f"Found {len(doctors)} doctors.")
        for d in doctors:
            print(f"- {d.user.username} (ID: {d.doctor_id})")
            
    except Exception as e:
        print(f"Error: {e}")
