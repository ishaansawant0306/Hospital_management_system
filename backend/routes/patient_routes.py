"""
Patient Routes Module
Handles all patient-facing API endpoints for the hospital management system.

This module provides functionality for:
- Patient dashboard and profile management
- Department and doctor browsing
- Appointment booking and management
- Medical history access
- Doctor search capabilities

Author: Ishaan Sawant
Date: November 2025
"""

# Core Flask imports for request handling
from flask import Blueprint, request, jsonify

# JWT authentication for securing endpoints
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

# SQLAlchemy query utilities
from sqlalchemy import or_  # For complex OR conditions in database queries

# Database models
from models.models import db, User, Doctor, Patient, Appointment, Treatment

# JSON parsing utilities
import json

# Import caching utility for performance optimization
from app_config import cache

# Create Blueprint for patient-specific routes
# All routes will be prefixed with '/patient'
patient_bp = Blueprint('patient_bp', __name__, url_prefix='/patient')


# ========== UTILITY FUNCTIONS ==========

def _extract_treatment_data(notes_json):
    """
    Parse and extract treatment notes from JSON string
    
    Treatment notes are stored as JSON in the database for flexibility.
    This helper safely parses the JSON and returns structured data.
    
    Args:
        notes_json (str or dict): JSON string or dictionary containing treatment notes
    
    Returns:
        dict: Structured treatment data with default values for missing fields
    """
    # Define default structure to ensure consistent response format
    default_structure = {
        'visitType': '',  # Type of medical visit
        'testDone': '',  # Medical tests performed
        'medicines': [],  # List of prescribed medications
        'notes': ''  # Additional doctor's notes
    }

    # Return default if no notes provided
    if not notes_json:
        return default_structure

    try:
        # Handle both string and dict inputs
        # Sometimes the data might already be parsed
        if isinstance(notes_json, str):
            parsed_data = json.loads(notes_json)
        else:
            parsed_data = notes_json

        # Extract fields with fallback to defaults
        extracted_data = {
            'visitType': parsed_data.get('visitType', ''),
            'testDone': parsed_data.get('testDone', ''),
            'medicines': parsed_data.get('medicines', []),
            'notes': parsed_data.get('notes', '')
        }
        
        return extracted_data
        
    except (json.JSONDecodeError, TypeError, AttributeError) as parse_error:
        # If parsing fails, log and return default structure
        # This prevents crashes from malformed data
        print(f"Warning: Failed to parse treatment notes: {parse_error}")
        return default_structure


def _extract_first_name(full_username):
    """
    Extract first name from username for personalized greetings
    
    Usernames in the system may use underscores or spaces as separators.
    This function handles both formats and returns a capitalized first name.
    
    Args:
        full_username (str): Full username from database
    
    Returns:
        str: Capitalized first name
    """
    # Handle empty or None username
    if not full_username:
        return 'Patient'
    
    # Check if username uses underscore separator
    if '_' in full_username:
        first_name = full_username.split('_')[0]
    # Otherwise assume space separator
    elif ' ' in full_username:
        first_name = full_username.split()[0]
    else:
        # Single word username
        first_name = full_username
    
    # Capitalize first letter for proper display
    return first_name.capitalize()


# ========== PATIENT DASHBOARD ENDPOINT ==========

@patient_bp.route('/dashboard', methods=['GET'])
@jwt_required()  # Requires valid JWT token in Authorization header
def get_patient_dashboard():
    """
    Retrieve patient dashboard information
    
    Returns basic patient profile data used to populate the dashboard.
    This is typically the first API call when a patient logs in.
    
    Returns:
        200: Patient profile data
        403: Unauthorized (not a patient)
        404: Patient profile not found
        500: Server error
    """
    try:
        # Extract JWT claims to verify identity and role
        jwt_claims = get_jwt()
        authenticated_user_id = get_jwt_identity()
        user_role = jwt_claims.get('role')

        # Authorization check: Only patients can access this endpoint
        if user_role != 'Patient':
            return jsonify({'error': 'Unauthorized: Patient access required'}), 403

        # Fetch patient record from database
        # Patient table links to User table via user_id foreign key
        patient_record = Patient.query.filter_by(user_id=authenticated_user_id).first()
        
        # Verify patient record exists
        if not patient_record:
            return jsonify({'error': 'Patient profile not found'}), 404

        # Extract username for processing
        full_username = patient_record.user.username if patient_record.user else ''
        
        # Extract first name for personalized greeting
        first_name = _extract_first_name(full_username)

        # Build response payload
        dashboard_data = {
            'patient': {
                'id': patient_record.id,
                'name': full_username,
                'first_name': first_name,  # Used for "Welcome, [Name]" message
                'age': patient_record.age,
                'gender': patient_record.gender,
                'contact_info': patient_record.contact_info
            }
        }
        
        return jsonify(dashboard_data), 200
        
    except Exception as error:
        # Log error for debugging
        print(f"Error in get_patient_dashboard: {str(error)}")
        import traceback
        traceback.print_exc()
        
        # Return generic error to client
        return jsonify({'error': f'Server error: {str(error)}'}), 500


# ========== DEPARTMENTS LISTING ENDPOINT ==========

@patient_bp.route('/departments', methods=['GET'])
@jwt_required()
def get_departments():
    """
    Get all available medical departments
    
    Dynamically generates department list based on doctor specializations.
    Only includes departments that have at least one active (non-blacklisted) doctor.
    
    This approach ensures the department list is always current and accurate.
    
    Returns:
        200: List of departments
        403: Unauthorized
        500: Server error
    """
    try:
        # Verify user authorization
        jwt_claims = get_jwt()
        user_role = jwt_claims.get('role')

        if user_role != 'Patient':
            return jsonify({'error': 'Unauthorized: Patient access required'}), 403

        # Query for unique specializations
        # Join with User table to exclude blacklisted doctors
        # Use distinct() to get only unique values
        specialization_query = db.session.query(Doctor.specialization).distinct()\
            .join(User, Doctor.user_id == User.id)\
            .filter(User.is_blacklisted == False)\
            .all()
        
        # Build departments list with proper formatting
        departments_list = []
        for index, (specialization,) in enumerate(specialization_query, start=1):
            # Skip null or empty specializations
            if specialization:
                department_entry = {
                    'id': index,  # Sequential ID for frontend
                    'name': specialization.title(),  # Capitalize for display
                    'key': specialization.lower()  # Lowercase for URL routing
                }
                departments_list.append(department_entry)
        
        # Sort alphabetically for better user experience
        departments_list.sort(key=lambda dept: dept['name'])
        
        return jsonify({'departments': departments_list}), 200
        
    except Exception as error:
        print(f"Error in get_departments: {str(error)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(error)}'}), 500


# ========== DOCTORS BY DEPARTMENT ENDPOINT ==========

@patient_bp.route('/departments/<department_name>/doctors', methods=['GET'])
@jwt_required()
# Note: Caching disabled during development for real-time updates
# TODO: Enable caching in production: @cache.cached(timeout=300)
def get_doctors_by_department(department_name):
    """
    Retrieve all doctors for a specific department
    
    Performs flexible, case-insensitive search for doctors by specialization.
    Includes mapping for common variations (e.g., "cardiology" matches "cardiologist").
    
    Args:
        department_name (str): Department name from URL path
    
    Returns:
        200: List of doctors in the department
        403: Unauthorized
        500: Server error
    """
    try:
        # Verify patient authorization
        jwt_claims = get_jwt()
        user_role = jwt_claims.get('role')

        if user_role != 'Patient':
            return jsonify({'error': 'Unauthorized: Patient access required'}), 403

        # Department name variations mapping
        # Allows matching different forms of the same specialization
        department_variations = {
            'cardiology': ['cardiology', 'cardiologist'],
            'oncology': ['oncology', 'oncologist'],
            'general': ['general', 'internal medicine', 'general medicine']
        }

        # Get search terms for this department
        search_terms = department_variations.get(
            department_name.lower(),
            [department_name.lower()]  # Default to department name if no mapping
        )
        
        # Build database query filters
        # Use ilike for case-insensitive LIKE queries
        query_filters = []
        for search_term in search_terms:
            # %term% allows partial matching
            query_filters.append(Doctor.specialization.ilike(f'%{search_term}%'))
        
        # Execute query with OR condition
        if query_filters:
            doctors_query_result = Doctor.query.filter(or_(*query_filters)).all()
        else:
            doctors_query_result = []
        
        # Debug logging
        print(f"Searching department '{department_name}' with terms: {search_terms}")
        print(f"Found {len(doctors_query_result)} doctors")

        # Build response list
        doctors_collection = []
        for doctor_record in doctors_query_result:
            # Filter out blacklisted doctors
            if doctor_record.user and not doctor_record.user.is_blacklisted:
                # Format doctor name with professional prefix
                doctor_username = doctor_record.user.username.replace('_', ' ').title()
                
                # Remove existing "Dr." prefix to avoid duplication
                if doctor_username.lower().startswith('dr.'):
                    doctor_username = doctor_username[3:].strip()
                
                # Add "Dr." prefix
                formatted_name = f"Dr. {doctor_username}"
                
                doctor_info = {
                    'id': doctor_record.id,
                    'name': formatted_name,
                    'specialization': doctor_record.specialization,
                    'doctor_id': doctor_record.doctor_id
                }
                doctors_collection.append(doctor_info)

        response_data = {
            'department': department_name,
            'doctors': doctors_collection
        }
        
        return jsonify(response_data), 200
        
    except Exception as error:
        print(f"Error in get_doctors_by_department: {str(error)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(error)}'}), 500


# ========== DOCTOR AVAILABILITY ENDPOINT ==========

@patient_bp.route('/doctors/<int:doctor_id>/availability', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60, query_string=True)  # Cache for 1 minute
def get_doctor_availability(doctor_id):
    """
    Check doctor's availability for next 7 days
    
    Combines doctor's set availability with existing bookings to show
    which time slots are actually available for new appointments.
    
    Time slots:
    - Morning: 08:00-12:00 (booked as 10:00)
    - Evening: 16:00-21:00 (booked as 18:00)
    
    Args:
        doctor_id (int): Doctor's database ID
    
    Returns:
        200: Availability schedule
        403: Unauthorized or doctor unavailable
        404: Doctor not found
        500: Server error
    """
    try:
        # Verify authorization
        jwt_claims = get_jwt()
        user_role = jwt_claims.get('role')

        if user_role != 'Patient':
            return jsonify({'error': 'Unauthorized: Patient access required'}), 403

        # Fetch doctor record
        doctor_record = Doctor.query.get(doctor_id)
        if not doctor_record:
            return jsonify({'error': 'Doctor not found'}), 404

        # Security check: Don't show blacklisted doctors
        if not doctor_record.user or doctor_record.user.is_blacklisted:
            return jsonify({'error': 'Doctor not available'}), 404

        # Parse doctor's availability schedule
        availability_schedule = []
        if doctor_record.availability:
            try:
                availability_schedule = json.loads(doctor_record.availability)
            except json.JSONDecodeError:
                # If parsing fails, treat as no availability
                availability_schedule = []

        # Generate next 7 days
        from datetime import date, timedelta
        current_date = date.today()
        availability_calendar = []
        
        for day_offset in range(7):
            # Calculate date
            target_date = current_date + timedelta(days=day_offset)
            date_string = target_date.strftime('%d/%m/%Y')
            
            # Find doctor's set availability for this date
            day_availability_settings = None
            for availability_entry in availability_schedule:
                if availability_entry.get('date') == date_string:
                    day_availability_settings = availability_entry
                    break
            
            # Check existing appointments
            existing_bookings = Appointment.query.filter(
                Appointment.doctor_id == doctor_id,
                Appointment.date == target_date,
                Appointment.status != 'Cancelled'
            ).all()
            
            # Determine booked slots
            morning_slot_booked = False
            evening_slot_booked = False
            
            for booking in existing_bookings:
                booking_hour = booking.time.hour
                
                # Morning: 08:00-12:00
                if 8 <= booking_hour < 12:
                    morning_slot_booked = True
                # Evening: 16:00-21:00
                elif 16 <= booking_hour < 21:
                    evening_slot_booked = True
            
            # Calculate final availability
            morning_available = False
            evening_available = False
            
            if day_availability_settings:
                morning_available = day_availability_settings.get('morning', False) and not morning_slot_booked
                evening_available = day_availability_settings.get('evening', False) and not evening_slot_booked
            
            # Add to calendar
            day_data = {
                'date': date_string,
                'morning': morning_available,
                'evening': evening_available,
                'morning_booked': morning_slot_booked,
                'evening_booked': evening_slot_booked
            }
            availability_calendar.append(day_data)

        # Build response
        response_payload = {
            'doctor': {
                'id': doctor_record.id,
                'name': doctor_record.user.username if doctor_record.user else None,
                'specialization': doctor_record.specialization
            },
            'availability': availability_calendar
        }
        
        return jsonify(response_payload), 200
        
    except Exception as error:
        print(f"Error in get_doctor_availability: {str(error)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(error)}'}), 500


# ========== APPOINTMENT BOOKING ENDPOINT ==========

@patient_bp.route('/appointments/book', methods=['POST'])
@jwt_required()
def book_appointment():
    """
    Book an appointment with a doctor
    
    Creates a new appointment record if the slot is available.
    
    Expected JSON:
    {
        "doctor_id": 123,
        "date": "24/01/2025",
        "time_slot": "morning"  # or "evening"
    }
    
    Returns:
        201: Appointment booked successfully
        400: Invalid input or slot already booked
        403: Unauthorized
        404: Doctor/Patient not found
        500: Server error
    """
    try:
        # Verify authorization
        jwt_claims = get_jwt()
        authenticated_user_id = get_jwt_identity()
        user_role = jwt_claims.get('role')

        if user_role != 'Patient':
            return jsonify({'error': 'Unauthorized: Patient access required'}), 403

        # Fetch patient profile
        patient_record = Patient.query.filter_by(user_id=authenticated_user_id).first()
        if not patient_record:
            return jsonify({'error': 'Patient profile not found'}), 404

        # Parse request data
        booking_data = request.get_json()
        doctor_id = booking_data.get('doctor_id')
        date_string = booking_data.get('date')  # Format: "24/01/2025"
        selected_slot = booking_data.get('time_slot')  # "morning" or "evening"

        # Validate required fields
        if not doctor_id or not date_string or not selected_slot:
            return jsonify({'error': 'Doctor ID, date, and time slot are required'}), 400

        # Validate slot value
        if selected_slot not in ['morning', 'evening']:
            return jsonify({'error': 'Time slot must be "morning" or "evening"'}), 400

        # Fetch doctor profile
        doctor_record = Doctor.query.get(doctor_id)
        if not doctor_record:
            return jsonify({'error': 'Doctor not found'}), 404

        # Security check: Prevent booking with blacklisted doctors
        if doctor_record.user and doctor_record.user.is_blacklisted:
            return jsonify({'error': 'This doctor is not available for appointments'}), 403

        # Parse appointment date
        from datetime import datetime, time
        try:
            appointment_date_obj = datetime.strptime(date_string, '%d/%m/%Y').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use DD/MM/YYYY'}), 400

        # Determine appointment time based on slot
        # Morning slot defaults to 10:00 AM
        # Evening slot defaults to 06:00 PM (18:00)
        if selected_slot == 'morning':
            appointment_time_obj = time(10, 0)
        else:
            appointment_time_obj = time(18, 0)

        # Check for existing booking (Double Booking Prevention)
        existing_booking = Appointment.query.filter_by(
            doctor_id=doctor_id,
            patient_id=patient_record.id,
            date=appointment_date_obj,
            time=appointment_time_obj,
            status='Booked'
        ).first()

        if existing_booking:
            return jsonify({'error': 'Appointment already exists for this time slot'}), 400

        # Create new appointment record
        new_appointment = Appointment(
            doctor_id=doctor_id,
            patient_id=patient_record.id,
            date=appointment_date_obj,
            time=appointment_time_obj,
            status='Booked'  # Default status
        )
        
        # Save to database
        db.session.add(new_appointment)
        db.session.commit()

        # Return success response
        return jsonify({
            'msg': 'Appointment booked successfully',
            'appointment': {
                'id': new_appointment.id,
                'doctor_id': doctor_id,
                'date': appointment_date_obj.isoformat(),
                'time': appointment_time_obj.strftime('%H:%M'),
                'status': 'Booked'
            }
        }), 201
        
    except Exception as error:
        # Rollback transaction on error
        db.session.rollback()
        print(f"Error in book_appointment: {str(error)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(error)}'}), 500


# ========== MEDICAL HISTORY ENDPOINT ==========

@patient_bp.route('/history', methods=['GET'])
@jwt_required()
def get_patient_history():
    """
    Retrieve patient's complete medical history
    
    Returns all appointments (past and upcoming) along with any 
    treatment records (diagnosis, prescription, notes).
    
    Returns:
        200: Medical history data
        403: Unauthorized
        404: Patient not found
        500: Server error
    """
    try:
        # Verify authorization
        jwt_claims = get_jwt()
        authenticated_user_id = get_jwt_identity()
        user_role = jwt_claims.get('role')

        if user_role != 'Patient':
            return jsonify({'error': 'Unauthorized: Patient access required'}), 403

        # Fetch patient profile
        patient_record = Patient.query.filter_by(user_id=authenticated_user_id).first()
        if not patient_record:
            return jsonify({'error': 'Patient profile not found'}), 404

        # Compile medical history from appointments
        medical_history_list = []
        
        # Iterate through all appointments associated with this patient
        for appointment_record in patient_record.appointments:
            # Basic appointment info
            history_entry = {
                'appointment_id': appointment_record.id,
                'date': appointment_record.date.isoformat(),
                'time': appointment_record.time.strftime('%H:%M'),
                'status': appointment_record.status,
                'doctor': appointment_record.doctor.user.username if appointment_record.doctor and appointment_record.doctor.user else None,
                'doctor_specialization': appointment_record.doctor.specialization if appointment_record.doctor else None,
            }
            
            # Add treatment details if available
            if appointment_record.treatment:
                # Parse JSON notes using helper
                treatment_notes = _extract_treatment_data(appointment_record.treatment.notes)
                
                history_entry['treatment'] = {
                    'diagnosis': appointment_record.treatment.diagnosis or '',
                    'prescription': appointment_record.treatment.prescription or '',
                    'notes': treatment_notes.get('notes', ''),
                    'visitType': treatment_notes.get('visitType', ''),
                    'testDone': treatment_notes.get('testDone', ''),
                    'medicines': treatment_notes.get('medicines', [])
                }
            
            medical_history_list.append(history_entry)

        # Build final response
        response_payload = {
            'patient': {
                'id': patient_record.id,
                'name': patient_record.user.username if patient_record.user else None,
                'age': patient_record.age,
                'gender': patient_record.gender,
                'contact_info': patient_record.contact_info
            },
            'medical_history': medical_history_list
        }
        
        return jsonify(response_payload), 200
        
    except Exception as error:
        print(f"Error in get_patient_history: {str(error)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(error)}'}), 500


# ========== EXPORT TREATMENTS ENDPOINT ==========

@patient_bp.route('/export/treatments', methods=['POST'])
@jwt_required()
def export_treatments():
    """
    Trigger CSV export of treatment history
    
    Initiates an asynchronous Celery task to generate a CSV file
    containing the patient's treatment history.
    
    Returns:
        202: Export task started
        403: Unauthorized
        500: Server error
    """
    try:
        # Verify authorization
        jwt_claims = get_jwt()
        authenticated_user_id = get_jwt_identity()
        user_role = jwt_claims.get('role')

        if user_role != 'Patient':
            return jsonify({'error': 'Unauthorized: Patient access required'}), 403

        # Import task here to avoid circular imports
        from tasks import export_patient_treatments
        
        # Trigger the Celery task asynchronously
        # .delay() puts the task in the queue
        async_task = export_patient_treatments.delay(authenticated_user_id)
        
        return jsonify({
            'message': 'Export started. You will be notified via email when it is ready.',
            'task_id': async_task.id
        }), 202
        
    except Exception as error:
        print(f"Error in export_treatments: {str(error)}")
        return jsonify({'error': f'Server error: {str(error)}'}), 500


# ========== DOCTOR SEARCH ENDPOINT ==========

@patient_bp.route('/search/doctors', methods=['GET'])
@jwt_required()
def search_doctors():
    """
    Search for doctors by name or specialization
    
    Allows patients to find doctors using a search query.
    Supports partial matching and case-insensitive search.
    
    Query Params:
        q (str): Search query string
        
    Returns:
        200: List of matching doctors
        403: Unauthorized
        500: Server error
    """
    try:
        # Verify authorization
        jwt_claims = get_jwt()
        user_role = jwt_claims.get('role')

        if user_role != 'Patient':
            return jsonify({'error': 'Unauthorized: Patient access required'}), 403

        # Get search query from URL parameters
        search_query = request.args.get('q', '').strip()
        
        print(f"[PATIENT SEARCH] Query: '{search_query}'")

        # Return empty list if no query provided
        if not search_query:
            return jsonify({'doctors': []}), 200

        # Prepare search variations
        # Handle both underscore and space separated names for flexibility
        query_with_underscore = search_query.replace(' ', '_')
        
        # Build complex query with OR conditions
        # Matches: Specialization OR Username (with spaces) OR Username (with underscores)
        matching_doctors = Doctor.query.filter(
            (Doctor.specialization.ilike(f'%{search_query}%')) |
            (Doctor.user.has(User.username.ilike(f'%{search_query}%'))) |
            (Doctor.user.has(User.username.ilike(f'%{query_with_underscore}%')))
        ).all()
        
        print(f"[PATIENT SEARCH] Found {len(matching_doctors)} doctors before filtering")

        # Process results and filter blacklisted doctors
        doctors_result_list = []
        for doctor_record in matching_doctors:
            # Skip if user account missing or blacklisted
            if doctor_record.user and not doctor_record.user.is_blacklisted:
                # Format name nicely
                username = doctor_record.user.username.replace('_', ' ').title()
                
                # Handle existing "Dr." prefix
                if username.lower().startswith('dr.'):
                    username = username[3:].strip()
                
                formatted_name = f"Dr. {username}"
                
                print(f"[PATIENT SEARCH] Adding: {formatted_name} - {doctor_record.specialization}")
                
                doctors_result_list.append({
                    'id': doctor_record.id,
                    'name': formatted_name,
                    'specialization': doctor_record.specialization,
                    'doctor_id': doctor_record.doctor_id
                })
        
        print(f"[PATIENT SEARCH] Returning {len(doctors_result_list)} doctors after filtering")

        return jsonify({'doctors': doctors_result_list}), 200
        
    except Exception as error:
        print(f"Error in search_doctors: {str(error)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(error)}'}), 500


# ========== CANCEL APPOINTMENT ENDPOINT ==========

@patient_bp.route('/appointments/<int:appointment_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_appointment(appointment_id):
    """
    Cancel a scheduled appointment
    
    Allows patients to cancel their own appointments.
    Completed appointments cannot be cancelled.
    
    Args:
        appointment_id (int): ID of appointment to cancel
        
    Returns:
        200: Cancellation successful
        400: Invalid state (already cancelled/completed)
        403: Unauthorized
        404: Appointment not found
        500: Server error
    """
    try:
        # Verify authorization
        jwt_claims = get_jwt()
        authenticated_user_id = get_jwt_identity()
        user_role = jwt_claims.get('role')

        if user_role != 'Patient':
            return jsonify({'error': 'Unauthorized: Patient access required'}), 403

        # Fetch patient profile
        patient_record = Patient.query.filter_by(user_id=authenticated_user_id).first()
        if not patient_record:
            return jsonify({'error': 'Patient profile not found'}), 404

        # Find appointment and verify ownership
        # Only the patient who booked it can cancel it
        appointment_record = Appointment.query.filter_by(
            id=appointment_id,
            patient_id=patient_record.id
        ).first()

        if not appointment_record:
            return jsonify({'error': 'Appointment not found or unauthorized'}), 404

        # Validate current status
        if appointment_record.status == 'Cancelled':
            return jsonify({'error': 'Appointment is already cancelled'}), 400
        
        if appointment_record.status == 'Completed':
            return jsonify({'error': 'Cannot cancel a completed appointment'}), 400

        # Update status
        appointment_record.status = 'Cancelled'
        db.session.commit()

        return jsonify({
            'msg': 'Appointment cancelled successfully',
            'appointment': {
                'id': appointment_record.id,
                'status': 'Cancelled'
            }
        }), 200
        
    except Exception as error:
        db.session.rollback()
        print(f"Error cancelling appointment: {str(error)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(error)}'}), 500


# ========== PROFILE UPDATE ENDPOINT ==========

@patient_bp.route('/profile', methods=['PATCH'])
@jwt_required()
def update_patient_profile():
    """
    Update patient profile information
    
    Allows patients to update their personal details.
    Sensitive fields like email/password are handled separately.
    
    Expected JSON (partial updates allowed):
    {
        "name": "New Name",
        "age": 30,
        "gender": "Male",
        "contact_info": "1234567890"
    }
    
    Returns:
        200: Profile updated successfully
        403: Unauthorized
        404: Patient not found
        500: Server error
    """
    try:
        # Verify authorization
        jwt_claims = get_jwt()
        authenticated_user_id = get_jwt_identity()
        user_role = jwt_claims.get('role')

        if user_role != 'Patient':
            return jsonify({'error': 'Unauthorized: Patient access required'}), 403

        # Fetch patient profile
        patient_record = Patient.query.filter_by(user_id=authenticated_user_id).first()
        if not patient_record:
            return jsonify({'error': 'Patient profile not found'}), 404

        # Parse update data
        update_data = request.get_json()

        # Apply updates if fields are present
        if 'name' in update_data:
            patient_record.user.username = update_data['name']
        if 'age' in update_data:
            patient_record.age = update_data['age']
        if 'gender' in update_data:
            patient_record.gender = update_data['gender']
        if 'contact_info' in update_data:
            patient_record.contact_info = update_data['contact_info']

        # Persist changes
        db.session.commit()

        # Return updated profile
        return jsonify({
            'msg': 'Profile updated successfully',
            'patient': {
                'id': patient_record.id,
                'name': patient_record.user.username,
                'age': patient_record.age,
                'gender': patient_record.gender,
                'contact_info': patient_record.contact_info
            }
        }), 200
        
    except Exception as error:
        db.session.rollback()
        print(f"Error updating patient profile: {str(error)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(error)}'}), 500
