"""
Doctor Routes Module
Handles all doctor-specific endpoints including login, dashboard, availability management,
appointment handling, and patient treatment records.
"""

# Flask imports for handling requests and responses
from flask import Blueprint, request, jsonify, current_app

# JWT imports for authentication and authorization
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, create_access_token

# Date/time utilities for handling appointment scheduling
from datetime import date, timedelta

# SQLAlchemy utilities for complex database queries
from sqlalchemy import and_  # Used for combining multiple filter conditions

# Database models
from models.models import db, User, Doctor, Patient, Appointment, Treatment

# JSON handling for storing/retrieving availability data
import json

# Security utilities for password verification
from werkzeug.security import check_password_hash

# Create Blueprint for doctor routes
# All routes in this file will be prefixed with '/doctor'
doctor_bp = Blueprint('doctor_bp', __name__, url_prefix='/doctor')

# ========== DOCTOR LOGIN ENDPOINT ==========
@doctor_bp.route('/login', methods=['POST'])
def doctor_login():
    """
    Doctor-specific login endpoint
    
    Authenticates doctors using email and password.
    Returns JWT token and doctor profile information.
    
    Expects JSON:
        - email (str): Doctor's email address
        - password (str): Doctor's password
    
    Returns:
        - 200: Login successful with token and profile
        - 400: Missing email or password
        - 401: Invalid credentials
        - 403: Doctor is blacklisted
    """
    # Parse request body
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Validate required fields
    if not email or not password:
        return jsonify({'msg': 'Email and password are required'}), 400

    # Find user with Doctor role
    # NOTE: We filter by role to ensure only doctors can login through this endpoint
    # Patients and admins have separate login endpoints
    user = User.query.filter_by(email=email, role='Doctor').first()
    
    # Verify user exists and password matches
    # check_password_hash compares hashed password securely
    if not user or not check_password_hash(user.password, password):
        return jsonify({'msg': 'Invalid credentials'}), 401

    # Security check: Prevent blacklisted doctors from logging in
    # Admins can blacklist doctors to revoke their access
    if user.is_blacklisted:
        return jsonify({'msg': 'You cannot login. You have been blacklisted'}), 403

    # Generate JWT access token
    # identity: user ID (used to identify user in protected routes)
    # additional_claims: extra data stored in token (role for authorization)
    access_token = create_access_token(
        identity=user.id,
        additional_claims={'role': user.role}
    )

    # Return success response with token and doctor profile
    # Frontend uses this data to populate the doctor dashboard
    return jsonify({
        'msg': 'Login successful',
        'access_token': access_token,
        'doctor': {
            'id': user.doctor.id,  # Doctor table ID
            'user_id': user.id,  # User table ID
            'name': user.username,
            'email': user.email,
            'specialization': user.doctor.specialization,
            'availability': user.doctor.availability  # JSON string of available slots
        }
    }), 200


# ========== DOCTOR DASHBOARD ENDPOINT ==========
@doctor_bp.route('/dashboard', methods=['GET'])
@jwt_required()  # Requires valid JWT token in Authorization header
def doctor_dashboard():
    """
    Get doctor dashboard data
    
    Returns:
        - Doctor profile information
        - Upcoming appointments (next 7 days)
        - List of assigned patients
    
    All data excludes blacklisted patients for security.
    """
    # Extract JWT claims and user identity
    claims = get_jwt()  # Get all claims from token
    current_user_id = get_jwt_identity()  # Get user ID from token
    current_role = claims.get('role')  # Get user role from claims

    # Debug logging for development
    # Helps troubleshoot authentication issues
    try:
        current_app.logger.debug('Doctor dashboard accessed - jwt claims: %s', claims)
        current_app.logger.debug('Current user id: %s, role: %s', current_user_id, current_role)
        auth_header = request.headers.get('Authorization')
        current_app.logger.debug('Authorization header present: %s', bool(auth_header))
    except Exception:
        # If logging fails, don't crash the endpoint
        # This can happen if logger is not configured
        pass

    # Authorization check: Only doctors can access this endpoint
    if current_role != 'Doctor':
        return jsonify({'error': 'Unauthorized: Doctor access required'}), 403

    # Fetch doctor profile from database
    doctor = Doctor.query.filter_by(user_id=current_user_id).first()
    if not doctor:
        return jsonify({'error': 'Doctor profile not found'}), 404

    # Calculate date range for upcoming appointments
    # Show appointments for the next 7 days only
    today = date.today()
    end_day = today + timedelta(days=7)

    # Query upcoming appointments with complex filtering
    # We use SQLAlchemy's and_() to combine multiple conditions:
    # 1. Appointments belong to this doctor
    # 2. Appointment date is within next 7 days
    # 3. Appointment is not cancelled or completed (only show active ones)
    appointments = (
        Appointment.query
        .filter(
            and_(
                Appointment.doctor_id == doctor.id,  # Only this doctor's appointments
                Appointment.date >= today,  # From today onwards
                Appointment.date <= end_day,  # Up to 7 days from now
                Appointment.status.notin_(['Cancelled', 'Completed'])  # Exclude finished appointments
            )
        )
        .order_by(Appointment.date.asc(), Appointment.time.asc())  # Sort by date, then time
        .all()
    )

    # Prepare data structures for response
    appointment_data = []  # List of appointment details
    patient_ids = set()  # Track unique patients (using set to avoid duplicates)

    # Process each appointment
    for a in appointments:
        # Fetch patient information for this appointment
        p = Patient.query.get(a.patient_id)
        
        # Security filter: Exclude blacklisted patients
        # Blacklisted patients should not appear in doctor's dashboard
        if p and p.user and not p.user.is_blacklisted:
            # Add patient to our unique set
            patient_ids.add(p.id)
            
            # Build appointment object for frontend
            appointment_data.append({
                'id': a.id,
                'date': a.date.isoformat(),  # Convert date to ISO format string (YYYY-MM-DD)
                'time': a.time.strftime('%H:%M'),  # Format time as HH:MM
                'status': a.status,
                'patient': {
                    'id': p.id,
                    'name': p.user.username if p.user else None,
                    'age': p.age,
                    'gender': p.gender,
                }
            })

    # Build list of assigned patients (patients with appointments)
    patients = []
    if patient_ids:
        # Fetch all unique patients in one query (more efficient than multiple queries)
        patient_rows = Patient.query.filter(Patient.id.in_(list(patient_ids))).all()
        
        for p in patient_rows:
            # Double-check blacklist status for security
            # This ensures no blacklisted patient data leaks through
            if p.user and not p.user.is_blacklisted:
                patients.append({
                    'id': p.id,
                    'name': p.user.username if p.user else None,
                    'age': p.age,
                    'gender': p.gender,
                    'contact_info': p.contact_info,
                })

    # Return complete dashboard data
    return jsonify({
        'doctor': {
            'id': doctor.id,
            'name': doctor.user.username,
            'specialization': doctor.specialization,
            'availability': doctor.availability  # JSON string of available time slots
        },
        'appointments_next_7_days': appointment_data,  # Upcoming appointments
        'assigned_patients': patients  # Unique patients with appointments
    }), 200


# ========== AVAILABILITY MANAGEMENT ENDPOINTS ==========

@doctor_bp.route('/availability', methods=['POST'])
@jwt_required()
def update_availability():
    """
    Update doctor's availability schedule
    
    Allows doctors to set their available time slots for the next 7 days.
    Availability is stored as JSON in the database for flexibility.
    
    Expected JSON format:
    {
        "availability": [
            {"date": "27/11/2025", "morning": true, "evening": false},
            {"date": "28/11/2025", "morning": true, "evening": true},
            ...
        ]
    }
    
    Time slots:
    - morning: 08:00 - 12:00
    - evening: 16:00 - 21:00
    
    Returns:
        200: Availability updated successfully
        400: Invalid data format
        403: Unauthorized
        404: Doctor not found
    """
    # Extract JWT claims for authorization
    claims = get_jwt()
    current_user_id = get_jwt_identity()
    current_role = claims.get('role')

    # Verify doctor role
    if current_role != 'Doctor':
        return jsonify({'error': 'Unauthorized: Doctor access required'}), 403

    # Fetch doctor profile
    doctor = Doctor.query.filter_by(user_id=current_user_id).first()
    if not doctor:
        return jsonify({'error': 'Doctor profile not found'}), 404

    # Parse request payload
    data = request.get_json()
    
    # Validate that availability data is present
    if not data or 'availability' not in data:
        return jsonify({'error': 'No availability data provided'}), 400

    # Store availability as JSON string in database
    # JSON format allows flexible storage of complex availability patterns
    # Alternative: Could use separate AvailabilitySlot table, but JSON is simpler
    import json
    doctor.availability = json.dumps(data['availability'])
    
    # Persist changes to database
    db.session.commit()

    # Return success response with updated availability
    return jsonify({
        'msg': 'Availability updated successfully',
        'availability': data['availability']
    }), 200


@doctor_bp.route('/availability', methods=['GET'])
@jwt_required()
def get_availability():
    """
    Retrieve doctor's current availability schedule
    
    Returns the doctor's set availability for the next 7 days.
    Used by the frontend to populate the availability modal.
    
    Returns:
        200: Availability data (array of day objects)
        403: Unauthorized
        404: Doctor not found
    """
    # Extract user identity from JWT
    claims = get_jwt()
    current_user_id = get_jwt_identity()
    current_role = claims.get('role')

    # Authorization check
    if current_role != 'Doctor':
        return jsonify({'error': 'Unauthorized: Doctor access required'}), 403

    # Fetch doctor record
    doctor = Doctor.query.filter_by(user_id=current_user_id).first()
    if not doctor:
        return jsonify({'error': 'Doctor profile not found'}), 404

    # Parse availability from JSON string
    # If no availability set, return empty array
    import json
    availability = json.loads(doctor.availability) if doctor.availability else []

    # Return availability data
    return jsonify({
        'availability': availability
    }), 200



# ========== APPOINTMENT STATUS MANAGEMENT ==========

@doctor_bp.route('/appointment/update-status', methods=['POST'])
@jwt_required()
def update_appointment_status():
    """
    Update appointment status (Complete or Cancel)
    
    Allows doctors to mark appointments as completed or cancelled.
    This is a critical workflow endpoint used after patient consultation.
    
    Expected JSON:
    {
        "appointment_id": 123,
        "status": "Completed"  # or "Cancelled"
    }
    
    Business rules:
    - Only the assigned doctor can update appointment status
    - Status must be either 'Completed' or 'Cancelled'
    - Completed appointments should have treatment records added
    
    Returns:
        200: Status updated successfully
        400: Invalid status value
        403: Unauthorized
        404: Appointment not found
    """
    # Get current user from JWT
    claims = get_jwt()
    current_user_id = get_jwt_identity()
    current_role = claims.get('role')

    # Verify doctor authorization
    if current_role != 'Doctor':
        return jsonify({'error': 'Unauthorized: Doctor access required'}), 403

    # Parse request data
    data = request.get_json()
    appointment_id = data.get('appointment_id')
    new_status = data.get('status')

    # Validate input
    # Only allow specific status values to maintain data integrity
    if not appointment_id or new_status not in ['Completed', 'Cancelled']:
        return jsonify({'error': 'Invalid input'}), 400

    # Get doctor profile
    doctor = Doctor.query.filter_by(user_id=current_user_id).first()
    if not doctor:
        return jsonify({'error': 'Doctor profile not found'}), 404

    # Fetch appointment and verify ownership
    # This prevents doctors from modifying other doctors' appointments
    appointment = Appointment.query.filter_by(id=appointment_id, doctor_id=doctor.id).first()
    if not appointment:
        return jsonify({'error': 'Appointment not found or unauthorized'}), 404

    # Update appointment status
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

    # Check if patient is blacklisted
    if patient.user and patient.user.is_blacklisted:
        return jsonify({'error': 'Patient record not accessible'}), 403

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
