from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy import or_
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


@patient_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_patient_dashboard():
    """
    Get the logged-in patient's dashboard data including name.
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

        # Extract first name from username
        username = patient.user.username if patient.user else ''
        first_name = username.split('_')[0] if '_' in username else username.split()[0] if username else 'Patient'
        first_name = first_name.capitalize()

        return jsonify({
            'patient': {
                'id': patient.id,
                'name': patient.user.username if patient.user else None,
                'first_name': first_name,
                'age': patient.age,
                'gender': patient.gender,
                'contact_info': patient.contact_info
            }
        }), 200
    except Exception as e:
        print(f"Error in get_patient_dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


from app_config import cache

@patient_bp.route('/departments/<department_name>/doctors', methods=['GET'])
@jwt_required()
@cache.cached(timeout=300, query_string=True)
def get_doctors_by_department(department_name):
    """
    Get doctors for a specific department/specialization.
    """
    try:
        claims = get_jwt()
        current_role = claims.get('role')

        if current_role != 'Patient':
            return jsonify({'error': 'Unauthorized: Patient access required'}), 403

        # Map department names to specializations (case-insensitive matching)
        # This allows matching doctors regardless of how specialization is stored
        department_mapping = {
            'cardiology': ['cardiology', 'cardiologist'],
            'oncology': ['oncology', 'oncologist'],
            'general': ['general', 'internal medicine', 'general medicine']
        }

        # Get base search term for this department (lowercase for case-insensitive search)
        search_terms = department_mapping.get(department_name.lower(), [department_name.lower()])
        
        # Build query to match any of the search terms (case-insensitive using ilike)
        filters = []
        for term in search_terms:
            # Use ilike for case-insensitive partial matching
            filters.append(Doctor.specialization.ilike(f'%{term}%'))
        
        # Query doctors by specialization (matching any term)
        if filters:
            doctors = Doctor.query.filter(or_(*filters)).all()
        else:
            doctors = []
        
        print(f"Searching for department '{department_name}' with terms: {search_terms}")
        print(f"Found {len(doctors)} doctors")
        for doc in doctors:
            print(f"  - {doc.user.username if doc.user else 'N/A'}: {doc.specialization}")

        doctors_list = []
        for doctor in doctors:
            if doctor.user and not doctor.user.is_blacklisted:
                # Format name: remove any existing "Dr." prefix, then add it once
                username = doctor.user.username.replace('_', ' ').title()
                # Remove "Dr." if it already exists in username
                if username.lower().startswith('dr.'):
                    username = username[3:].strip()
                doctor_name = f"Dr. {username}"
                
                doctors_list.append({
                    'id': doctor.id,
                    'name': doctor_name,
                    'specialization': doctor.specialization,
                    'doctor_id': doctor.doctor_id
                })

        return jsonify({
            'department': department_name,
            'doctors': doctors_list
        }), 200
    except Exception as e:
        print(f"Error in get_doctors_by_department: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@patient_bp.route('/doctors/<int:doctor_id>/availability', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60, query_string=True) # Cache for 1 minute as availability changes often
def get_doctor_availability(doctor_id):
    """
    Get a specific doctor's availability for the next 7 days.
    Also checks existing appointments to mark slots as unavailable.
    """
    try:
        claims = get_jwt()
        current_role = claims.get('role')

        if current_role != 'Patient':
            return jsonify({'error': 'Unauthorized: Patient access required'}), 403

        # Get the doctor
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404

        if not doctor.user or doctor.user.is_blacklisted:
            return jsonify({'error': 'Doctor not available'}), 404

        # Parse doctor's availability
        import json
        availability_data = []
        if doctor.availability:
            try:
                availability_data = json.loads(doctor.availability)
            except:
                availability_data = []

        # Generate next 7 days
        from datetime import date, timedelta
        today = date.today()
        availability_days = []
        
        for i in range(7):
            day_date = today + timedelta(days=i)
            day_str = day_date.strftime('%d/%m/%Y')
            
            # Find matching availability entry
            day_availability = None
            for avail in availability_data:
                if avail.get('date') == day_str:
                    day_availability = avail
                    break
            
            # Check existing appointments for this doctor on this date
            existing_appointments = Appointment.query.filter(
                Appointment.doctor_id == doctor_id,
                Appointment.date == day_date,
                Appointment.status != 'Cancelled'
            ).all()
            
            # Determine which slots are booked
            morning_booked = False
            evening_booked = False
            for appt in existing_appointments:
                appt_time = appt.time
                hours = appt_time.hour
                # Morning: 08:00 - 12:00
                if 8 <= hours < 12:
                    morning_booked = True
                # Evening: 16:00 - 21:00
                elif 16 <= hours < 21:
                    evening_booked = True
            
            # Determine availability
            morning_available = False
            evening_available = False
            
            if day_availability:
                morning_available = day_availability.get('morning', False) and not morning_booked
                evening_available = day_availability.get('evening', False) and not evening_booked
            else:
                # If no availability set, both slots are unavailable
                morning_available = False
                evening_available = False

            availability_days.append({
                'date': day_str,
                'morning': morning_available,
                'evening': evening_available,
                'morning_booked': morning_booked,
                'evening_booked': evening_booked
            })

        return jsonify({
            'doctor': {
                'id': doctor.id,
                'name': doctor.user.username if doctor.user else None,
                'specialization': doctor.specialization
            },
            'availability': availability_days
        }), 200
    except Exception as e:
        print(f"Error in get_doctor_availability: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@patient_bp.route('/appointments/book', methods=['POST'])
@jwt_required()
def book_appointment():
    """
    Book an appointment with a doctor.
    Expects JSON payload:
    {
        "doctor_id": 123,
        "date": "24/01/2025",
        "time_slot": "morning" or "evening"
    }
    """
    try:
        claims = get_jwt()
        current_user_id = get_jwt_identity()
        current_role = claims.get('role')

        if current_role != 'Patient':
            return jsonify({'error': 'Unauthorized: Patient access required'}), 403

        # Get the patient
        patient = Patient.query.filter_by(user_id=current_user_id).first()
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404

        data = request.get_json()
        doctor_id = data.get('doctor_id')
        date_str = data.get('date')  # Format: "24/01/2025"
        time_slot = data.get('time_slot')  # "morning" or "evening"

        if not doctor_id or not date_str or not time_slot:
            return jsonify({'error': 'Doctor ID, date, and time slot are required'}), 400

        if time_slot not in ['morning', 'evening']:
            return jsonify({'error': 'Time slot must be "morning" or "evening"'}), 400

        # Get the doctor
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404

        # Parse date
        from datetime import datetime, time
        try:
            appointment_date = datetime.strptime(date_str, '%d/%m/%Y').date()
        except:
            return jsonify({'error': 'Invalid date format. Use DD/MM/YYYY'}), 400

        # Set time based on slot
        if time_slot == 'morning':
            appointment_time = time(10, 0)  # 10:00 AM (middle of morning slot)
        else:
            appointment_time = time(18, 0)  # 6:00 PM (middle of evening slot)

        # Check if appointment already exists
        existing = Appointment.query.filter_by(
            doctor_id=doctor_id,
            patient_id=patient.id,
            date=appointment_date,
            time=appointment_time,
            status='Booked'
        ).first()

        if existing:
            return jsonify({'error': 'Appointment already exists for this time slot'}), 400

        # Create new appointment
        appointment = Appointment(
            doctor_id=doctor_id,
            patient_id=patient.id,
            date=appointment_date,
            time=appointment_time,
            status='Booked'
        )
        db.session.add(appointment)
        db.session.commit()

        return jsonify({
            'msg': 'Appointment booked successfully',
            'appointment': {
                'id': appointment.id,
                'doctor_id': doctor_id,
                'date': appointment_date.isoformat(),
                'time': appointment_time.strftime('%H:%M'),
                'status': 'Booked'
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error in book_appointment: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


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


@patient_bp.route('/export/treatments', methods=['POST'])
@jwt_required()
def export_treatments():
    """
    Trigger async task to export patient treatments to CSV.
    """
    try:
        claims = get_jwt()
        current_user_id = get_jwt_identity()
        current_role = claims.get('role')

        if current_role != 'Patient':
            return jsonify({'error': 'Unauthorized: Patient access required'}), 403

        # Import here to avoid circular imports if any
        from tasks import export_patient_treatments
        
        # Trigger the Celery task
        task = export_patient_treatments.delay(current_user_id)
        
        return jsonify({
            'message': 'Export started. You will be notified via email when it is ready.',
            'task_id': task.id
        }), 202
    except Exception as e:
        print(f"Error in export_treatments: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500
