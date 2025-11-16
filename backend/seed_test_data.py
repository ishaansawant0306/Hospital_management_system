#!/usr/bin/env python
"""
Test Data Seeder - Creates test doctor, patients, and appointments for development

This script sets up demo data so you can immediately see the Doctor Dashboard working.
Run this after starting the Flask app.
"""

import sys
import os
from datetime import datetime, timedelta, time

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app_config import app, db
from models.models import User, Doctor, Patient, Appointment
from werkzeug.security import generate_password_hash


def seed_test_data():
    """Create test doctor, patients, and appointments"""
    
    with app.app_context():
        # Check if test doctor already exists
        test_doctor_user = User.query.filter_by(email='doctor@hospital.com').first()
        
        if test_doctor_user:
            print(f"✓ Test doctor user already exists (ID: {test_doctor_user.id})")
            doctor = test_doctor_user.doctor
            if not doctor:
                print("! Doctor profile missing, creating...")
                doctor = Doctor(
                    user_id=test_doctor_user.id,
                    specialization="Cardiology",
                    availability='{"Monday": ["09:00", "17:00"], "Tuesday": ["09:00", "17:00"]}'
                )
                db.session.add(doctor)
                db.session.commit()
                print(f"✓ Created doctor profile (ID: {doctor.id})")
        else:
            print("Creating test doctor...")
            test_doctor_user = User(
                username='doctor_test',
                email='doctor@hospital.com',
                password=generate_password_hash('doc123'),
                role='Doctor'
            )
            db.session.add(test_doctor_user)
            db.session.commit()
            print(f"✓ Created doctor user (ID: {test_doctor_user.id})")
            
            doctor = Doctor(
                user_id=test_doctor_user.id,
                specialization="Cardiology",
                availability='{"Monday": ["09:00", "17:00"], "Tuesday": ["09:00", "17:00"]}'
            )
            db.session.add(doctor)
            db.session.commit()
            print(f"✓ Created doctor profile (ID: {doctor.id})")
        
        # Create test patients
        patient_emails = [
            ('patient1@hospital.com', 'John Doe', 35, 'Male'),
            ('patient2@hospital.com', 'Jane Smith', 28, 'Female'),
            ('patient3@hospital.com', 'Mike Johnson', 45, 'Male'),
        ]
        
        patients = []
        for email, name, age, gender in patient_emails:
            existing = User.query.filter_by(email=email).first()
            if existing:
                print(f"✓ Patient {name} already exists")
                patients.append(existing.patient)
            else:
                print(f"Creating patient {name}...")
                user = User(
                    username=name.lower().replace(' ', '_'),
                    email=email,
                    password=generate_password_hash('patient123'),
                    role='Patient'
                )
                db.session.add(user)
                db.session.commit()
                
                patient = Patient(
                    user_id=user.id,
                    age=age,
                    gender=gender,
                    contact_info=f'+1-555-{1000 + user.id}'
                )
                db.session.add(patient)
                db.session.commit()
                print(f"✓ Created patient {name} (ID: {patient.id})")
                patients.append(patient)
        
        # Create appointments for the next 7 days
        today = datetime.now().date()
        appointment_times = [
            time(9, 0),   # 9:00 AM
            time(10, 30), # 10:30 AM
            time(14, 0),  # 2:00 PM
            time(15, 30), # 3:30 PM
        ]
        
        statuses = ['Booked', 'Completed']
        
        print("\nCreating appointments...")
        appt_count = 0
        for i, patient in enumerate(patients):
            for day_offset in range(7):
                # Skip some appointments to make it realistic
                if (i + day_offset) % 3 == 0:
                    appt_date = today + timedelta(days=day_offset)
                    appt_time = appointment_times[day_offset % len(appointment_times)]
                    status = statuses[day_offset % len(statuses)]
                    
                    # Check if already exists
                    existing = Appointment.query.filter_by(
                        doctor_id=doctor.id,
                        patient_id=patient.id,
                        date=appt_date,
                        time=appt_time
                    ).first()
                    
                    if not existing:
                        appointment = Appointment(
                            doctor_id=doctor.id,
                            patient_id=patient.id,
                            date=appt_date,
                            time=appt_time,
                            status=status
                        )
                        db.session.add(appointment)
                        appt_count += 1
        
        db.session.commit()
        print(f"✓ Created {appt_count} appointments")
        
        # Print summary
        print("\n" + "="*60)
        print("TEST DATA CREATED SUCCESSFULLY!")
        print("="*60)
        print(f"Doctor: doctor@hospital.com (password: doc123)")
        print(f"  - Specialization: Cardiology")
        print(f"  - Assigned Patients: {len(patients)}")
        print(f"  - Total Appointments: {Appointment.query.filter_by(doctor_id=doctor.id).count()}")
        print("\nTest Patients:")
        for patient in patients:
            print(f"  - {patient.user.username} ({patient.user.email})")
        print("\nNow login with: doctor@hospital.com / doc123")
        print("You should see appointments and patient data in the Doctor Dashboard!")
        print("="*60)


if __name__ == '__main__':
    seed_test_data()
