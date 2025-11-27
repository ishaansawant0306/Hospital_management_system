from app_config import app
from models.models import db, Appointment
from datetime import date, time, timedelta

with app.app_context():
    doctor_id = 3
    patient_id = 3
    base_date = date.today()
    times = [time(10, 0), time(11, 30), time(14, 0)]
    created = []
    for idx, t in enumerate(times, start=1):
        appt_date = base_date + timedelta(days=idx)
        appt = Appointment(doctor_id=doctor_id, patient_id=patient_id,
                           date=appt_date, time=t, status='Booked')
        db.session.add(appt)
        created.append((appt_date.isoformat(), t.strftime('%H:%M')))
    db.session.commit()
    print('Created appointments:', created)
