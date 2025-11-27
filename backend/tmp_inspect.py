from app_config import app
from models.models import db, Doctor, Patient, Appointment, User
from datetime import date, time, timedelta

with app.app_context():
    doctors = [(d.id, d.user.username if d.user else None) for d in Doctor.query.all()]
    patients = [(p.id, p.user.username if p.user else None) for p in Patient.query.all()]
    appts = [(a.id, a.doctor_id, a.patient_id, a.date.isoformat(), a.time.strftime('%H:%M'), a.status) for a in Appointment.query.order_by(Appointment.date).all()]
    print('Doctors:', doctors)
    print('Patients:', patients)
    print('Appointments:', appts)
