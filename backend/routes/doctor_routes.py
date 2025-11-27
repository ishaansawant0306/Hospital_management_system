from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import date, timedelta
from sqlalchemy import and_
from models.models import db, User, Doctor, Patient, Appointment, Treatment
import json

doctor_bp = Blueprint('doctor_bp', __name__, url_prefix='/doctor')

from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token

@doctor_bp.route('/login', methods=['POST'])
def doctor_login():
    """Doctor login using email + password."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'msg': 'Email and password are required'}), 400

    # Find user with role Doctor
    user = User.query.filter_by(email=email, role='Doctor').first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'msg': 'Invalid credentials'}), 401

    # Create JWT token
    access_token = create_access_token(identity=user.id, additional_claims={'role': user.role})

    return jsonify({
        'msg': 'Login successful',
        'access_token': access_token,
        'doctor': {
            'id': user.doctor.id,
            'user_id': user.id,
            'name': user.username,
            'email': user.email,
            'specialization': user.doctor.specialization,
            'availability': user.doctor.availability
        }
    }), 200


@doctor_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def doctor_dashboard():
    claims = get_jwt()
    current_user_id = get_jwt_identity()
    current_role = claims.get('role')

    # Debug logging to inspect JWT claims and role during development
    try:
        current_app.logger.debug('Doctor dashboard accessed - jwt claims: %s', claims)
        current_app.logger.debug('Current user id: %s, role: %s', current_user_id, current_role)
        auth_header = request.headers.get('Authorization')
        current_app.logger.debug('Authorization header present: %s', bool(auth_header))
    except Exception:
        # If logging fails for any reason, don't break the route
        pass

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
    Expects JSON payload with array of availability objects:
    {
        "availability": [
            {"date": "27/11/2025", "morning": true, "evening": false},
            {"date": "28/11/2025", "morning": true, "evening": true},
            ...
        ]
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
    if not data or 'availability' not in data:
        return jsonify({'error': 'No availability data provided'}), 400

    # Convert availability array to JSON string and store
    import json
    doctor.availability = json.dumps(data['availability'])
    db.session.commit()

    return jsonify({
        'msg': 'Availability updated successfully',
        'availability': data['availability']
    }), 200


@doctor_bp.route('/availability', methods=['GET'])
@jwt_required()
def get_availability():
    """Get doctor's current availability."""
    claims = get_jwt()
    current_user_id = get_jwt_identity()
    current_role = claims.get('role')

    if current_role != 'Doctor':
        return jsonify({'error': 'Unauthorized: Doctor access required'}), 403

    doctor = Doctor.query.filter_by(user_id=current_user_id).first()
    if not doctor:
        return jsonify({'error': 'Doctor profile not found'}), 404

    import json
    availability = json.loads(doctor.availability) if doctor.availability else []

    return jsonify({
        'availability': availability
    }), 200



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


def _parse_treatment_notes(notes):
    """Helper to safely parse treatment.notes JSON payload."""
    default_payload = {
        'visitType': '',
        'testDone': '',
        'medicines': [],
        'notes': ''
    }

    if not notes:
        return default_payload

    try:
        payload = json.loads(notes)
        if isinstance(payload, dict):
            default_payload.update({
                key: payload.get(key, default_payload[key])
                for key in default_payload.keys()
            })
    except (ValueError, TypeError):
        pass

    return default_payload


def _doctor_and_appointment_for_current_user(appointment_id):
    """Fetch doctor & appointment for the current JWT identity."""
    claims = get_jwt()
    current_user_id = get_jwt_identity()
    current_role = claims.get('role')

    if current_role != 'Doctor':
        return None, None, jsonify({'error': 'Unauthorized: Doctor access required'}), 403

    doctor = Doctor.query.filter_by(user_id=current_user_id).first()
    if not doctor:
        return None, None, jsonify({'error': 'Doctor profile not found'}), 404

    appointment = Appointment.query.filter_by(id=appointment_id, doctor_id=doctor.id).first()
    if not appointment:
        return None, None, jsonify({'error': 'Appointment not found or unauthorized'}), 404

    return doctor, appointment, None, None


@doctor_bp.route('/treatment/<int:appointment_id>', methods=['GET'])
@jwt_required()
def get_treatment_details(appointment_id):
    doctor, appointment, error_response, status_code = _doctor_and_appointment_for_current_user(appointment_id)
    if error_response:
        return error_response, status_code

    treatment = appointment.treatment
    if not treatment:
        return jsonify({'treatment': None}), 200

    notes_payload = _parse_treatment_notes(treatment.notes)
    response_payload = {
        'appointment_id': appointment.id,
        'visitType': notes_payload.get('visitType', ''),
        'testDone': notes_payload.get('testDone', ''),
        'diagnosis': treatment.diagnosis or '',
        'medicines': notes_payload.get('medicines', []),
        'prescription': treatment.prescription or '',
        'notes': notes_payload.get('notes', '')
    }

    return jsonify({'treatment': response_payload}), 200


@doctor_bp.route('/treatment/<int:appointment_id>', methods=['POST'])
@jwt_required()
def save_treatment_details(appointment_id):
    doctor, appointment, error_response, status_code = _doctor_and_appointment_for_current_user(appointment_id)
    if error_response:
        return error_response, status_code

    data = request.get_json() or {}
    medicines = data.get('medicines') or []
    if not isinstance(medicines, list):
        medicines = []

    notes_payload = {
        'visitType': data.get('visitType', ''),
        'testDone': data.get('testDone', ''),
        'medicines': medicines,
        'notes': data.get('notes', '')
    }

    treatment = appointment.treatment
    if not treatment:
        treatment = Treatment(appointment_id=appointment.id)

    treatment.diagnosis = data.get('diagnosis', '') or ''
    treatment.prescription = data.get('prescription', '') or ''
    treatment.notes = json.dumps(notes_payload)

    db.session.add(treatment)
    db.session.commit()

    response_payload = {
        'appointment_id': appointment.id,
        'visitType': notes_payload['visitType'],
        'testDone': notes_payload['testDone'],
        'diagnosis': treatment.diagnosis,
        'medicines': medicines,
        'prescription': treatment.prescription,
        'notes': notes_payload['notes']
    }

    return jsonify({'msg': 'Treatment saved successfully', 'treatment': response_payload}), 200


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
            notes_payload = _parse_treatment_notes(appt.treatment.notes)
            record['treatment'] = {
                'diagnosis': appt.treatment.diagnosis,
                'prescription': appt.treatment.prescription,
                'notes': notes_payload.get('notes', ''),
                'visitType': notes_payload.get('visitType', ''),
                'testDone': notes_payload.get('testDone', ''),
                'medicines': notes_payload.get('medicines', [])
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
