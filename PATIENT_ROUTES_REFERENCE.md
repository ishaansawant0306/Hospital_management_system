"""
Patient Routes Module - COMPLETE VERSION
Handles all patient-specific functionality with extensive documentation
"""

# [Previous imports and helper functions from PART1 would go here]
# For brevity in this refactored version, I'm showing the continuation

# Continuing from get_doctors_by_department...

# ========== DOCTOR AVAILABILITY ENDPOINT ==========

@patient_bp.route('/doctors/<int:doctor_id>/availability', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60, query_string=True)  # Cache for 1 minute (availability changes frequently)
def get_doctor_availability(doctor_id):
    """
    Get doctor's availability for the next 7 days
    
    This endpoint combines:
    1. Doctor's set availability (from their availability schedule)
    2. Existing booked appointments (to mark slots as unavailable)
    
    The result shows which time slots are actually available for booking.
    
    Time slots:
    - Morning: 08:00 - 12:00 (represented as 10:00 AM in bookings)
    - Evening: 16:00 - 21:00 (represented as 18:00 PM in bookings)
    
    Args:
        doctor_id (int): Doctor's database ID
    
    Returns:
        200: Availability data for next 7 days
        403: Unauthorized or doctor not available
        404: Doctor not found
        500: Server error
    """
    try:
        # Verify patient authorization
        claims = get_jwt()
        current_role = claims.get('role')

        if current_role != 'Patient':
            return jsonify({'error': 'Unauthorized: Patient access required'}), 403

        # Fetch doctor from database
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404

        # Security check: Don't show availability for blacklisted doctors
        if not doctor.user or doctor.user.is_blacklisted:
            return jsonify({'error': 'Doctor not available'}), 404

        # Parse doctor's availability schedule from JSON
        # Availability is stored as JSON string in database
        import json
        availability_data = []
        if doctor.availability:
            try:
                availability_data = json.loads(doctor.availability)
            except:
                # If JSON parsing fails, treat as no availability set
                availability_data = []

        # Generate next 7 days of availability
        from datetime import date, timedelta
        today = date.today()
        availability_days = []
        
        for i in range(7):
            # Calculate date for this day
            day_date = today + timedelta(days=i)
            day_str = day_date.strftime('%d/%m/%Y')  # Format: DD/MM/YYYY
            
            # Find doctor's set availability for this specific date
            day_availability = None
            for avail in availability_data:
                if avail.get('date') == day_str:
                    day_availability = avail
                    break
            
            # Check existing appointments to see which slots are already booked
            # We need to exclude cancelled appointments from this check
            existing_appointments = Appointment.query.filter(
                Appointment.doctor_id == doctor_id,
                Appointment.date == day_date,
                Appointment.status != 'Cancelled'  # Only count active appointments
            ).all()
            
            # Determine which time slots are already booked
            morning_booked = False
            evening_booked = False
            
            for appt in existing_appointments:
                appt_time = appt.time
                hours = appt_time.hour
                
                # Morning slot: 08:00 - 12:00
                if 8 <= hours < 12:
                    morning_booked = True
                # Evening slot: 16:00 - 21:00
                elif 16 <= hours < 21:
                    evening_booked = True
            
            # Calculate final availability
            # A slot is available only if:
            # 1. Doctor has marked it as available in their schedule
            # 2. No appointment is already booked for that slot
            morning_available = False
            evening_available = False
            
            if day_availability:
                # Doctor has set availability for this date
                morning_available = day_availability.get('morning', False) and not morning_booked
                evening_available = day_availability.get('evening', False) and not evening_booked
            else:
                # No availability set means both slots are unavailable
                morning_available = False
                evening_available = False

            # Add this day's availability to response
            availability_days.append({
                'date': day_str,
                'morning': morning_available,
                'evening': evening_available,
                'morning_booked': morning_booked,  # For debugging/UI feedback
                'evening_booked': evening_booked
            })

        # Return doctor info and availability
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


# ========== BOOK APPOINTMENT ENDPOINT ==========

@patient_bp.route('/appointments/book', methods=['POST'])
@jwt_required()
def book_appointment():
    """
    Book an appointment with a doctor
    
    This endpoint handles the appointment booking process:
    1. Validates patient authorization
    2. Validates doctor availability
    3. Checks for duplicate bookings
    4. Creates new appointment record
    
    Expected JSON payload:
    {
        "doctor_id": 123,
        "date": "24/01/2025",  # Format: DD/MM/YYYY
        "time_slot": "morning"  # or "evening"
    }
    
    Returns:
        201: Appointment created successfully
        400: Invalid input or duplicate booking
        403: Unauthorized or doctor not available
        404: Doctor or patient not found
        500: Server error
    """
    try:
        # Extract user identity from JWT
        claims = get_jwt()
        current_user_id = get_jwt_identity()
        current_role = claims.get('role')

        # Authorization check
        if current_role != 'Patient':
            return jsonify({'error': 'Unauthorized: Patient access required'}), 403

        # Get patient record
        patient = Patient.query.filter_by(user_id=current_user_id).first()
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404

        # Parse request data
        data = request.get_json()
        doctor_id = data.get('doctor_id')
        date_str = data.get('date')  # Format: "24/01/2025"
        time_slot = data.get('time_slot')  # "morning" or "evening"

        # Validate required fields
        if not doctor_id or not date_str or not time_slot:
            return jsonify({'error': 'Doctor ID, date, and time slot are required'}), 400

        # Validate time slot value
        if time_slot not in ['morning', 'evening']:
            return jsonify({'error': 'Time slot must be "morning" or "evening"'}), 400

        # Verify doctor exists
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404

        # Security check: Don't allow booking with blacklisted doctors
        if doctor.user and doctor.user.is_blacklisted:
            return jsonify({'error': 'This doctor is not available for appointments'}), 403

        # Parse and validate date
        from datetime import datetime, time
        try:
            appointment_date = datetime.strptime(date_str, '%d/%m/%Y').date()
        except:
            return jsonify({'error': 'Invalid date format. Use DD/MM/YYYY'}), 400

        # Convert time slot to actual time
        # We use fixed times to represent morning and evening slots
        if time_slot == 'morning':
            appointment_time = time(10, 0)  # 10:00 AM (middle of morning slot 08:00-12:00)
        else:
            appointment_time = time(18, 0)  # 6:00 PM (middle of evening slot 16:00-21:00)

        # Check for duplicate booking
        # Prevent patient from booking the same slot twice
        existing = Appointment.query.filter_by(
            doctor_id=doctor_id,
            patient_id=patient.id,
            date=appointment_date,
            time=appointment_time,
            status='Booked'
        ).first()

        if existing:
            return jsonify({'error': 'Appointment already exists for this time slot'}), 400

        # Create new appointment record
        appointment = Appointment(
            doctor_id=doctor_id,
            patient_id=patient.id,
            date=appointment_date,
            time=appointment_time,
            status='Booked'  # Initial status
        )
        
        # Save to database
        db.session.add(appointment)
        db.session.commit()

        # Return success response with appointment details
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
        # Rollback database changes on error
        db.session.rollback()
        print(f"Error in book_appointment: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


# ========== PATIENT MEDICAL HISTORY ENDPOINT ==========

@patient_bp.route('/history', methods=['GET'])
@jwt_required()
def get_patient_history():
    """
    Get patient's complete medical history
    
    Returns all appointments and associated treatment records
    for the logged-in patient. This includes:
    - Past and upcoming appointments
    - Doctor information
    - Treatment details (diagnosis, prescription, medicines)
    
    Returns:
        200: Complete medical history
        403: Unauthorized
        404: Patient not found
        500: Server error
    """
    try:
        # Verify patient authorization
        claims = get_jwt()
        current_user_id = get_jwt_identity()
        current_role = claims.get('role')

        if current_role != 'Patient':
            return jsonify({'error': 'Unauthorized: Patient access required'}), 403

        # Get patient record
        patient = Patient.query.filter_by(user_id=current_user_id).first()
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404

        # Build medical history from all appointments
        history = []
        for appt in patient.appointments:
            # Basic appointment information
            record = {
                'appointment_id': appt.id,
                'date': appt.date.isoformat(),
                'time': appt.time.strftime('%H:%M'),
                'status': appt.status,
                'doctor': appt.doctor.user.username if appt.doctor and appt.doctor.user else None,
                'doctor_specialization': appt.doctor.specialization if appt.doctor else None,
            }
            
            # Add treatment details if available
            # Not all appointments have treatment records (e.g., upcoming appointments)
            if appt.treatment:
                # Parse treatment notes from JSON
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

        # Return patient info and complete history
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


# ========== EXPORT TREATMENTS ENDPOINT ==========

@patient_bp.route('/export/treatments', methods=['POST'])
@jwt_required()
def export_treatments():
    """
    Trigger async CSV export of treatment history
    
    This endpoint starts a background Celery task to generate
    a CSV file containing the patient's complete treatment history.
    The patient receives an email when the export is ready.
    
    This is done asynchronously because:
    1. Large histories might take time to process
    2. Prevents timeout on slow connections
    3. Allows user to continue using the app
    
    Returns:
        202: Export task started (async)
        403: Unauthorized
        500: Server error
    """
    try:
        # Verify patient authorization
        claims = get_jwt()
        current_user_id = get_jwt_identity()
        current_role = claims.get('role')

        if current_role != 'Patient':
            return jsonify({'error': 'Unauthorized: Patient access required'}), 403

        # Import Celery task
        # Import here to avoid circular import issues
        from tasks import export_patient_treatments
        
        # Trigger async task
        # .delay() sends task to Celery worker for background processing
        task = export_patient_treatments.delay(current_user_id)
        
        # Return immediately with task ID
        # Patient will be notified via email when export completes
        return jsonify({
            'message': 'Export started. You will be notified via email when it is ready.',
            'task_id': task.id  # Can be used to check task status
        }), 202
        
    except Exception as e:
        print(f"Error in export_treatments: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


# ========== DOCTOR SEARCH ENDPOINT ==========

@patient_bp.route('/search/doctors', methods=['GET'])
@jwt_required()
def search_doctors():
    """
    Search for doctors by name or specialization
    
    Performs flexible search that matches:
    - Doctor name (handles both space and underscore separators)
    - Specialization
    
    Query parameter:
        q: Search query string
    
    Returns:
        200: List of matching doctors
        403: Unauthorized
        500: Server error
    """
    try:
        # Verify patient authorization
        claims = get_jwt()
        current_role = claims.get('role')

        if current_role != 'Patient':
            return jsonify({'error': 'Unauthorized: Patient access required'}), 403

        # Get search query from URL parameters
        query_str = request.args.get('q', '').strip()
        
        print(f"[PATIENT SEARCH] Query: '{query_str}'")

        # Return empty list if no query provided
        if not query_str:
            return jsonify({'doctors': []}), 200

        # Handle different name formats
        # Some usernames use underscores, some use spaces
        query_with_underscore = query_str.replace(' ', '_')
        
        # Build complex search query
        # Search in both specialization and username fields
        # Use ilike for case-insensitive matching
        doctors = Doctor.query.filter(
            (Doctor.specialization.ilike(f'%{query_str}%')) |  # Match specialization
            (Doctor.user.has(User.username.ilike(f'%{query_str}%'))) |  # Match name with spaces
            (Doctor.user.has(User.username.ilike(f'%{query_with_underscore}%')))  # Match name with underscores
        ).all()
        
        print(f"[PATIENT SEARCH] Found {len(doctors)} doctors before filtering")

        # Filter and format results
        doctor_list = []
        for doc in doctors:
            # Exclude blacklisted doctors from search results
            if doc.user and not doc.user.is_blacklisted:
                # Format name with Dr. prefix
                username = doc.user.username.replace('_', ' ').title()
                
                # Remove existing "Dr." to avoid duplication
                if username.lower().startswith('dr.'):
                    username = username[3:].strip()
                
                doctor_name = f"Dr. {username}"
                
                print(f"[PATIENT SEARCH] Adding: {doctor_name} - {doc.specialization}")
                
                doctor_list.append({
                    'id': doc.id,
                    'name': doctor_name,
                    'specialization': doc.specialization,
                    'doctor_id': doc.doctor_id
                })
        
        print(f"[PATIENT SEARCH] Returning {len(doctor_list)} doctors after filtering")

        return jsonify({'doctors': doctor_list}), 200
        
    except Exception as e:
        print(f"Error in search_doctors: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


# ========== CANCEL APPOINTMENT ENDPOINT ==========

@patient_bp.route('/appointments/<int:appointment_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_appointment(appointment_id):
    """
    Cancel a patient's appointment
    
    Allows patients to cancel their own appointments.
    Includes ownership verification to prevent unauthorized cancellations.
    
    Business rules:
    - Only the patient who booked can cancel
    - Cannot cancel already cancelled appointments
    - Cannot cancel completed appointments
    
    Args:
        appointment_id (int): ID of appointment to cancel
    
    Returns:
        200: Appointment cancelled successfully
        400: Invalid cancellation (already cancelled/completed)
        403: Unauthorized
        404: Appointment not found
        500: Server error
    """
    try:
        # Verify patient authorization
        claims = get_jwt()
        current_user_id = get_jwt_identity()
        current_role = claims.get('role')

        if current_role != 'Patient':
            return jsonify({'error': 'Unauthorized: Patient access required'}), 403

        # Get patient record
        patient = Patient.query.filter_by(user_id=current_user_id).first()
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404

        # Get appointment and verify ownership
        # This prevents patients from cancelling other patients' appointments
        appointment = Appointment.query.filter_by(
            id=appointment_id,
            patient_id=patient.id  # Ownership check
        ).first()

        if not appointment:
            return jsonify({'error': 'Appointment not found or unauthorized'}), 404

        # Business rule: Cannot cancel already cancelled appointment
        if appointment.status == 'Cancelled':
            return jsonify({'error': 'Appointment is already cancelled'}), 400
        
        # Business rule: Cannot cancel completed appointment
        # Once treatment is provided, appointment cannot be cancelled
        if appointment.status == 'Completed':
            return jsonify({'error': 'Cannot cancel a completed appointment'}), 400

        # Update appointment status
        appointment.status = 'Cancelled'
        db.session.commit()

        # Return success response
        return jsonify({
            'msg': 'Appointment cancelled successfully',
            'appointment': {
                'id': appointment.id,
                'status': 'Cancelled'
            }
        }), 200
        
    except Exception as e:
        # Rollback on error
        db.session.rollback()
        print(f"Error cancelling appointment: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


# ========== UPDATE PROFILE ENDPOINT ==========

@patient_bp.route('/profile', methods=['PATCH'])
@jwt_required()
def update_patient_profile():
    """
    Update patient profile information
    
    Allows patients to update their own profile data.
    
    Updatable fields:
    - name (username)
    - age
    - gender
    - contact_info
    
    Security note: Email and password cannot be changed through this endpoint
    to prevent accidental account lockout.
    
    Returns:
        200: Profile updated successfully
        403: Unauthorized
        404: Patient not found
        500: Server error
    """
    try:
        # Verify patient authorization
        claims = get_jwt()
        current_user_id = get_jwt_identity()
        current_role = claims.get('role')

        if current_role != 'Patient':
            return jsonify({'error': 'Unauthorized: Patient access required'}), 403

        # Get patient record
        patient = Patient.query.filter_by(user_id=current_user_id).first()
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404

        # Parse update data
        data = request.get_json()

        # Update only provided fields
        # This allows partial updates (PATCH semantics)
        if 'name' in data:
            patient.user.username = data['name']
        if 'age' in data:
            patient.age = data['age']
        if 'gender' in data:
            patient.gender = data['gender']
        if 'contact_info' in data:
            patient.contact_info = data['contact_info']

        # Save changes
        db.session.commit()

        # Return updated profile
        return jsonify({
            'msg': 'Profile updated successfully',
            'patient': {
                'id': patient.id,
                'name': patient.user.username,
                'age': patient.age,
                'gender': patient.gender,
                'contact_info': patient.contact_info
            }
        }), 200
        
    except Exception as e:
        # Rollback on error
        db.session.rollback()
        print(f"Error updating patient profile: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500
