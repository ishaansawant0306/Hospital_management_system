from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import date, timedelta
from sqlalchemy import and_
from models.models import db, User, Doctor, Patient, Appointment

doctor_bp = Blueprint('doctor_bp', __name__, url_prefix='/doctor')

@doctor_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def doctor_dashboard():
    claims = get_jwt()
    current_user_id = get_jwt_identity()
    current_role = claims.get('role')

    if current_role != 'Doctor':
        return jsonify({'error': 'Unauthorized: Doctor access required'}), 403

    doctor = Doctor.query.filter_by(user_id=current_user_id).first()
    if not doctor:
        return jsonify({'error': 'Doctor profile not found'}), 404

    today = date.today()
    end_day = today + timedelta(days=7)

    appointments = (
        Appointment.query
        .filter(
            and_(
                Appointment.doctor_id == doctor.id,
                Appointment.date >= today,
                Appointment.date <= end_day,
                Appointment.status != 'Cancelled'
            )
        )
        .order_by(Appointment.date.asc(), Appointment.time.asc())
        .all()
    )

    appointment_data = []
    patient_ids = set()

    for a in appointments:
        p = Patient.query.get(a.patient_id)
        if p:
            patient_ids.add(p.id)
            appointment_data.append({
                'id': a.id,
                'date': a.date.isoformat(),
                'time': a.time.strftime('%H:%M'),
                'status': a.status,
                'patient': {
                    'id': p.id,
                    'name': p.user.username if p.user else None,
                    'age': p.age,
                    'gender': p.gender,
                }
            })

    patients = []
    if patient_ids:
        patient_rows = Patient.query.filter(Patient.id.in_(list(patient_ids))).all()
        for p in patient_rows:
            patients.append({
                'id': p.id,
                'name': p.user.username if p.user else None,
                'age': p.age,
                'gender': p.gender,
                'contact_info': p.contact_info,
            })

    return jsonify({
        'doctor': {
            'id': doctor.id,
            'name': doctor.user.username,
            'specialization': doctor.specialization,
            'availability': doctor.availability
        },
        'appointments_next_7_days': appointment_data,
        'assigned_patients': patients
    }), 200

@doctor_bp.route('/availability', methods=['POST'])
@jwt_required()
def update_availability():
    """
    Update doctor's availability for the next 7 days.
    Expects JSON payload with keys like:
    {
        "Monday": ["10:00", "14:00"],
        "Tuesday": ["11:00"],
        ...
    }
    """
    claims = get_jwt()
    current_user_id = get_jwt_identity()
    current_role = claims.get('role')

    if current_role != 'Doctor':
        return jsonify({'error': 'Unauthorized: Doctor access required'}), 403

    doctor = Doctor.query.filter_by(user_id=current_user_id).first()
    if not doctor:
        return jsonify({'error': 'Doctor profile not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No availability data provided'}), 400

    # Convert dict to JSON string and store
    import json
    doctor.availability = json.dumps(data)
    db.session.commit()

    return jsonify({'msg': 'Availability updated successfully'}), 200

@doctor_bp.route('/appointment/update-status', methods=['POST'])
@jwt_required()
def update_appointment_status():
    """
    Update status of an appointment (Completed or Cancelled).
    Expects JSON payload:
    {
        "appointment_id": 123,
        "status": "Completed"  # or "Cancelled"
    }
    """
    claims = get_jwt()
    current_user_id = get_jwt_identity()
    current_role = claims.get('role')

    if current_role != 'Doctor':
        return jsonify({'error': 'Unauthorized: Doctor access required'}), 403

    data = request.get_json()
    appointment_id = data.get('appointment_id')
    new_status = data.get('status')

    if not appointment_id or new_status not in ['Completed', 'Cancelled']:
        return jsonify({'error': 'Invalid input'}), 400

    doctor = Doctor.query.filter_by(user_id=current_user_id).first()
    if not doctor:
        return jsonify({'error': 'Doctor profile not found'}), 404

    appointment = Appointment.query.filter_by(id=appointment_id, doctor_id=doctor.id).first()
    if not appointment:
        return jsonify({'error': 'Appointment not found or unauthorized'}), 404

    appointment.status = new_status
    db.session.commit()

    return jsonify({'msg': f'Appointment status updated to {new_status}'}), 200

@doctor_bp.route('/treatment/add', methods=['POST'])
@jwt_required()
def add_treatment():
    """
    Add treatment details for a completed appointment.
    Expects JSON payload:
    {
        "appointment_id": 123,
        "diagnosis": "Flu",
        "prescription": "Paracetamol 500mg",
        "notes": "Rest and hydration"
    }
    """
    claims = get_jwt()
    current_user_id = get_jwt_identity()
    current_role = claims.get('role')

    if current_role != 'Doctor':
        return jsonify({'error': 'Unauthorized: Doctor access required'}), 403

    data = request.get_json()
    appointment_id = data.get('appointment_id')
    diagnosis = data.get('diagnosis')
    prescription = data.get('prescription')
    notes = data.get('notes')

    if not appointment_id or not diagnosis:
        return jsonify({'error': 'Appointment ID and diagnosis are required'}), 400

    doctor = Doctor.query.filter_by(user_id=current_user_id).first()
    if not doctor:
        return jsonify({'error': 'Doctor profile not found'}), 404

    appointment = Appointment.query.filter_by(id=appointment_id, doctor_id=doctor.id).first()
    if not appointment:
        return jsonify({'error': 'Appointment not found or unauthorized'}), 404

    # Ensure appointment is marked Completed before adding treatment
    if appointment.status != 'Completed':
        return jsonify({'error': 'Treatment can only be added to Completed appointments'}), 400

    from models.models import Treatment
    treatment = Treatment(
        appointment_id=appointment.id,
        diagnosis=diagnosis,
        prescription=prescription,
        notes=notes
    )
    db.session.add(treatment)
    db.session.commit()

    return jsonify({'msg': 'Treatment record added successfully'}), 201

@doctor_bp.route('/patient/history/<int:patient_id>', methods=['GET'])
@jwt_required()
def patient_history(patient_id):
    """
    Fetch full medical history of a patient.
    Accessible only to Doctors.
    Returns all appointments + treatment records.
    """
    claims = get_jwt()
    current_user_id = get_jwt_identity()
    current_role = claims.get('role')

    if current_role != 'Doctor':
        return jsonify({'error': 'Unauthorized: Doctor access required'}), 403

    doctor = Doctor.query.filter_by(user_id=current_user_id).first()
    if not doctor:
        return jsonify({'error': 'Doctor profile not found'}), 404

    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404

    history = []
    for appt in patient.appointments:
        record = {
            'appointment_id': appt.id,
            'date': appt.date.isoformat(),
            'time': appt.time.strftime('%H:%M'),
            'status': appt.status,
            'doctor': appt.doctor.user.username if appt.doctor and appt.doctor.user else None,
        }
        if appt.treatment:
            record['treatment'] = {
                'diagnosis': appt.treatment.diagnosis,
                'prescription': appt.treatment.prescription,
                'notes': appt.treatment.notes
            }
        history.append(record)

    return jsonify({
        'patient': {
            'id': patient.id,
            'name': patient.user.username if patient.user else None,
            'age': patient.age,
            'gender': patient.gender,
            'contact_info': patient.contact_info
        },
        'medical_history': history
    }), 200
