from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.models import db, User, Doctor, Patient, Appointment, Treatment
import json

patient_bp = Blueprint('patient_bp', __name__, url_prefix='/patient')


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
        if isinstance(notes, str):
            parsed = json.loads(notes)
        else:
            parsed = notes

        return {
            'visitType': parsed.get('visitType', ''),
            'testDone': parsed.get('testDone', ''),
            'medicines': parsed.get('medicines', []),
            'notes': parsed.get('notes', '')
        }
    except (json.JSONDecodeError, TypeError, AttributeError):
        return default_payload


@patient_bp.route('/history', methods=['GET'])
@jwt_required()
def get_patient_history():
    """
    Get the logged-in patient's own medical history.
    Returns all appointments + treatment records for the current patient.
    """
    try:
        claims = get_jwt()
        current_user_id = get_jwt_identity()
        current_role = claims.get('role')

        if current_role != 'Patient':
            return jsonify({'error': 'Unauthorized: Patient access required'}), 403

        # Get the patient record for the current user
        patient = Patient.query.filter_by(user_id=current_user_id).first()
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404

        # Get all appointments for this patient
        history = []
        for appt in patient.appointments:
            record = {
                'appointment_id': appt.id,
                'date': appt.date.isoformat(),
                'time': appt.time.strftime('%H:%M'),
                'status': appt.status,
                'doctor': appt.doctor.user.username if appt.doctor and appt.doctor.user else None,
                'doctor_specialization': appt.doctor.specialization if appt.doctor else None,
            }
            if appt.treatment:
                notes_payload = _parse_treatment_notes(appt.treatment.notes)
                record['treatment'] = {
                    'diagnosis': appt.treatment.diagnosis or '',
                    'prescription': appt.treatment.prescription or '',
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
    except Exception as e:
        print(f"Error in get_patient_history: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

