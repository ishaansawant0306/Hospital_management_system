
from app_config import app
from models.models import Doctor, User

with app.app_context():
    print("Checking for doctor with ID 'DOC-2345'...")
    doctor = Doctor.query.filter_by(doctor_id='DOC-2345').first()
    if doctor:
        print(f"Found Doctor: ID={doctor.id}, Name={doctor.user.username}, Specialization={doctor.specialization}")
    else:
        print("Doctor with ID 'DOC-2345' NOT found.")

    print("\nListing all doctors:")
    doctors = Doctor.query.all()
    for d in doctors:
        print(f"- ID: {d.doctor_id}, Name: {d.user.username}, Spec: {d.specialization}")
