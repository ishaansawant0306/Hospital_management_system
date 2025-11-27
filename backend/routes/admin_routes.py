"""
Admin Management Routes

Provides endpoints for admin dashboard:
- List, create, update, delete doctors
- List, create, update, delete patients  
- List, filter appointments
- Search doctors and patients
- Blacklist/unblacklist users
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models.models import db, User, Doctor, Patient, Appointment
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import json

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/api/admin')


def check_admin_role(claims):
    """Helper to verify admin role from JWT claims."""
    if claims.get('role') != 'Admin':
        return False
    return True


# ============================================================================
# DOCTORS ENDPOINTS
# ============================================================================

@admin_bp.route('/doctors', methods=['GET'])
@jwt_required()
def list_doctors():
    """Get all doctors with details."""
    claims = get_jwt()
    if not check_admin_role(claims):
        return jsonify({'error': 'Unauthorized: Admin only'}), 403

    try:
        doctors = Doctor.query.all()
        doctor_list = []
        for doc in doctors:
            doctor_list.append({
                'id': doc.id,
                'user_id': doc.user_id,
                'doctor_id': doc.doctor_id,
                'name': doc.user.username if doc.user else 'N/A',
                'email': doc.user.email if doc.user else 'N/A',
                'specialization': doc.specialization,
                'availability': doc.availability,
                'address': doc.address if doc.address else 'N/A',
                'contact_info': getattr(doc.user, 'contact_info', 'N/A') if doc.user else 'N/A',
                'is_blacklisted': doc.user.is_blacklisted if doc.user else False
            })
        return jsonify({'doctors': doctor_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/doctors', methods=['POST'])      # Create a new doctor
@jwt_required()
def create_doctor():
    """Create a new doctor profile (Admin only)."""
    claims = get_jwt()
    if not check_admin_role(claims):
        return jsonify({'error': 'Unauthorized: Admin only'}), 403

    try:
        data = request.get_json()

        # Validate required fields
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        doctor_id = data.get('doctor_id')  # Unique doctor ID
        specialization = data.get('specialization')
        availability = data.get('availability', '{}')
        address = data.get('address', '')  # Optional address

        # Check all required fields
        if not name or not specialization:
            return jsonify({'msg': 'Name and specialization are required'}), 400
        
        if not email:
            return jsonify({'msg': 'Email is required'}), 400
            
        if not password:
            return jsonify({'msg': 'Password is required'}), 400
            
        if not doctor_id:
            return jsonify({'msg': 'Doctor ID is required'}), 400

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'msg': 'Email already exists'}), 400
            
        # Check if doctor_id already exists
        if Doctor.query.filter_by(doctor_id=doctor_id).first():
            return jsonify({'msg': 'Doctor ID already exists. Please use a unique ID.'}), 400

        # Generate base username from name
        username = name.lower().replace(' ', '_')
        base_username = username

        # Ensure username uniqueness
        i = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}{i}"
            i += 1

        # Create User with Doctor role
        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),  # Hash password securely
            role='Doctor'
        )
        db.session.add(user)
        db.session.flush()  # Get the user ID before commit

        # Create Doctor record linked to User
        doctor = Doctor(
            user_id=user.id,
            doctor_id=doctor_id,
            specialization=specialization,
            availability=availability,
            address=address
        )
        db.session.add(doctor)
        db.session.commit()

        return jsonify({
            'msg': 'Doctor created successfully',
            'doctor': {
                'id': doctor.id,
                'user_id': user.id,
                'doctor_id': doctor.doctor_id,
                'name': user.username,
                'email': user.email,
                'specialization': specialization,
                'availability': availability,
                'address': address
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/doctors/<int:doctor_id>', methods=['PATCH'])
@jwt_required()
def update_doctor(doctor_id):
    """Update doctor profile."""
    claims = get_jwt()
    if not check_admin_role(claims):
        return jsonify({'error': 'Unauthorized: Admin only'}), 403

    try:
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404

        data = request.get_json()

        # Update doctor fields
        if 'specialization' in data:
            doctor.specialization = data['specialization']
        if 'availability' in data:
            doctor.availability = data['availability']
        if 'doctor_id' in data:
            # Check for uniqueness if changing doctor_id
            if doctor.doctor_id != data['doctor_id']:
                existing = Doctor.query.filter_by(doctor_id=data['doctor_id']).first()
                if existing:
                    return jsonify({'error': 'Doctor ID already exists'}), 400
            doctor.doctor_id = data['doctor_id']
        if 'address' in data:
            doctor.address = data['address']

        # Update user fields if provided
        if 'name' in data:
            doctor.user.username = data['name']
        # Email update is restricted by frontend but backend should handle it if sent
        if 'email' in data:
            # Check uniqueness
            if doctor.user.email != data['email']:
                existing = User.query.filter_by(email=data['email']).first()
                if existing:
                    return jsonify({'error': 'Email already exists'}), 400
            doctor.user.email = data['email']

        db.session.commit()

        return jsonify({
            'msg': 'Doctor updated successfully',
            'doctor': {
                'id': doctor.id,
                'user_id': doctor.user_id,
                'name': doctor.user.username,
                'email': doctor.user.email,
                'specialization': doctor.specialization,
                'availability': doctor.availability,
                'doctor_id': getattr(doctor, 'doctor_id', None),
                'address': getattr(doctor, 'address', None)
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/doctors/<int:doctor_id>', methods=['DELETE'])
@jwt_required()
def delete_doctor(doctor_id):
    """Delete a doctor and associated user, plus related appointments."""
    claims = get_jwt()
    if not check_admin_role(claims):
        return jsonify({'error': 'Unauthorized: Admin only'}), 403

    try:
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404

        user_id = doctor.user_id
        
        # First delete all appointments associated with this doctor
        Appointment.query.filter_by(doctor_id=doctor_id).delete()
        
        # Delete the doctor record
        db.session.delete(doctor)
        
        # Also delete the associated user
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)

        db.session.commit()

        return jsonify({'msg': 'Doctor deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================================
# PATIENTS ENDPOINTS
# ============================================================================

@admin_bp.route('/patients', methods=['GET'])
@jwt_required()
def list_patients():
    """Get all patients with details."""
    claims = get_jwt()
    if not check_admin_role(claims):
        return jsonify({'error': 'Unauthorized: Admin only'}), 403

    try:
        patients = Patient.query.all()
        patient_list = []
        for pat in patients:
            patient_list.append({
                'id': pat.id,
                'user_id': pat.user_id,
                'name': pat.user.username if pat.user else 'N/A',
                'email': pat.user.email if pat.user else 'N/A',
                'age': pat.age,
                'gender': pat.gender,
                'contact_info': pat.contact_info,
                'is_blacklisted': pat.user.is_blacklisted if pat.user else False
            })
        return jsonify({'patients': patient_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/patients/<int:patient_id>', methods=['PATCH'])
@jwt_required()
def update_patient(patient_id):
    """Update patient profile."""
    claims = get_jwt()
    if not check_admin_role(claims):
        return jsonify({'error': 'Unauthorized: Admin only'}), 403

    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404

        data = request.get_json()

        # Update patient fields
        if 'age' in data:
            patient.age = data['age']
        if 'gender' in data:
            patient.gender = data['gender']
        if 'contact_info' in data:
            patient.contact_info = data['contact_info']
        if 'name' in data:
            patient.user.username = data['name']
        if 'email' in data:
            patient.user.email = data['email']

        db.session.commit()

        return jsonify({
            'msg': 'Patient updated successfully',
            'patient': {
                'id': patient.id,
                'user_id': patient.user_id,
                'name': patient.user.username,
                'email': patient.user.email,
                'age': patient.age,
                'gender': patient.gender,
                'contact_info': patient.contact_info
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/patients/<int:patient_id>', methods=['DELETE'])
@jwt_required()
def delete_patient(patient_id):
    """Delete a patient and associated user, plus related appointments."""
    claims = get_jwt()
    if not check_admin_role(claims):
        return jsonify({'error': 'Unauthorized: Admin only'}), 403

    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404

        user_id = patient.user_id
        
        # First delete all appointments associated with this patient
        Appointment.query.filter_by(patient_id=patient_id).delete()
        
        # Delete the patient record
        db.session.delete(patient)
        
        # Also delete the associated user
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)

        db.session.commit()

        return jsonify({'msg': 'Patient deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================================
# APPOINTMENTS ENDPOINTS
# ============================================================================

@admin_bp.route('/appointments', methods=['GET'])
@jwt_required()
def list_appointments():
    """Get all appointments with filters."""
    claims = get_jwt()
    if not check_admin_role(claims):
        return jsonify({'error': 'Unauthorized: Admin only'}), 403

    try:
        # Optional filters
        status = request.args.get('status')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        query = Appointment.query

        if status:
            query = query.filter_by(status=status)

        if date_from:
            query = query.filter(Appointment.date >= datetime.fromisoformat(date_from).date())

        if date_to:
            query = query.filter(Appointment.date <= datetime.fromisoformat(date_to).date())

        appointments = query.order_by(Appointment.date.desc()).all()

        appt_list = []
        for appt in appointments:
            appt_list.append({
                'id': appt.id,
                'patient': appt.patient.user.username if appt.patient and appt.patient.user else 'N/A',
                'patient_id': appt.patient_id,
                'doctor': appt.doctor.user.username if appt.doctor and appt.doctor.user else 'N/A',
                'doctor_id': appt.doctor_id,
                'date': appt.date.isoformat(),
                'time': appt.time.isoformat(),
                'status': appt.status
            })

        return jsonify({'appointments': appt_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/appointments/<int:appt_id>', methods=['PATCH'])
@jwt_required()
def update_appointment(appt_id):
    """Update appointment status."""
    claims = get_jwt()
    if not check_admin_role(claims):
        return jsonify({'error': 'Unauthorized: Admin only'}), 403

    try:
        appointment = Appointment.query.get(appt_id)
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404

        data = request.get_json()

        if 'status' in data:
            appointment.status = data['status']

        db.session.commit()

        return jsonify({
            'msg': 'Appointment updated successfully',
            'appointment': {
                'id': appointment.id,
                'status': appointment.status
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/appointments/<int:appt_id>/detail', methods=['GET'])
@jwt_required()
def get_appointment_detail(appt_id):
    """Get single appointment with patient and doctor details."""
    claims = get_jwt()
    if not check_admin_role(claims):
        return jsonify({'error': 'Unauthorized: Admin only'}), 403

    try:
        appointment = Appointment.query.get(appt_id)
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404

        # Build appointment response with full details
        appt_detail = {
            'id': appointment.id,
            'patient': {
                'id': appointment.patient_id,
                'name': appointment.patient.user.username if appointment.patient and appointment.patient.user else 'N/A',
                'email': appointment.patient.user.email if appointment.patient and appointment.patient.user else 'N/A',
                'age': appointment.patient.age if appointment.patient else None,
                'gender': appointment.patient.gender if appointment.patient else None,
                'contact_info': appointment.patient.contact_info if appointment.patient else 'N/A'
            },
            'doctor': {
                'id': appointment.doctor_id,
                'name': appointment.doctor.user.username if appointment.doctor and appointment.doctor.user else 'N/A',
                'email': appointment.doctor.user.email if appointment.doctor and appointment.doctor.user else 'N/A',
                'specialization': appointment.doctor.specialization if appointment.doctor else 'N/A'
            },
            'date': appointment.date.isoformat() if appointment.date else None,
            'time': appointment.time.isoformat() if appointment.time else None,
            'reason': appointment.reason if hasattr(appointment, 'reason') else 'N/A',
            'status': appointment.status,
            'notes': appointment.notes if hasattr(appointment, 'notes') else 'N/A'
        }

        return jsonify({'appointment': appt_detail}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/appointments/<int:appt_id>', methods=['DELETE'])
@jwt_required()
def delete_appointment(appt_id):
    """Delete an appointment."""
    claims = get_jwt()
    if not check_admin_role(claims):
        return jsonify({'error': 'Unauthorized: Admin only'}), 403

    try:
        appointment = Appointment.query.get(appt_id)
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404

        db.session.delete(appointment)
        db.session.commit()

        return jsonify({'msg': 'Appointment deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================================
# SEARCH ENDPOINTS
# ============================================================================

@admin_bp.route('/search/doctors', methods=['GET'])
@jwt_required()
def search_doctors():
    """Search doctors by name or specialization."""
    claims = get_jwt()
    if not check_admin_role(claims):
        return jsonify({'error': 'Unauthorized: Admin only'}), 403

    try:
        query_str = request.args.get('q', '').lower()

        if not query_str:
            return jsonify({'doctors': []}), 200

        # Search in doctor name (via user.username) or specialization
        doctors = Doctor.query.filter(
            (Doctor.specialization.ilike(f'%{query_str}%')) |
            (Doctor.user.has(User.username.ilike(f'%{query_str}%')))
        ).all()

        doctor_list = []
        for doc in doctors:
            doctor_list.append({
                'id': doc.id,
                'user_id': doc.user_id,
                'name': doc.user.username if doc.user else 'N/A',
                'email': doc.user.email if doc.user else 'N/A',
                'specialization': doc.specialization,
                'availability': doc.availability,
                'is_blacklisted': doc.user.is_blacklisted if doc.user else False
            })

        return jsonify({'doctors': doctor_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/search/patients', methods=['GET'])
@jwt_required()
def search_patients():
    """Search patients by name, email, or contact info."""
    claims = get_jwt()
    if not check_admin_role(claims):
        return jsonify({'error': 'Unauthorized: Admin only'}), 403

    try:
        query_str = request.args.get('q', '').lower()

        if not query_str:
            return jsonify({'patients': []}), 200

        # Search in patient name (via user.username), email, contact info, or ID
        criteria = (
            (Patient.user.has(User.username.ilike(f'%{query_str}%'))) |
            (Patient.user.has(User.email.ilike(f'%{query_str}%'))) |
            (Patient.contact_info.ilike(f'%{query_str}%'))
        )

        # If query is numeric, also check ID
        if query_str.isdigit():
            criteria = criteria | (Patient.id == int(query_str))

        patients = Patient.query.filter(criteria).all()

        patient_list = []
        for pat in patients:
            patient_list.append({
                'id': pat.id,
                'user_id': pat.user_id,
                'name': pat.user.username if pat.user else 'N/A',
                'email': pat.user.email if pat.user else 'N/A',
                'age': pat.age,
                'gender': pat.gender,
                'contact_info': pat.contact_info
                
            })

        return jsonify({'patients': patient_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# BLACKLIST ENDPOINTS
# ============================================================================

@admin_bp.route('/blacklist/doctor/<int:doctor_id>', methods=['POST'])
@jwt_required()
def blacklist_doctor(doctor_id):
    """Blacklist a doctor by doctor_id."""
    claims = get_jwt()
    if not check_admin_role(claims):
        return jsonify({'error': 'Unauthorized: Admin only'}), 403

    try:
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404

        user = doctor.user
        if not user:
            return jsonify({'error': 'Associated user not found'}), 404

        # Mark user as blacklisted
        user.is_blacklisted = True
        db.session.commit()

        return jsonify({'msg': f'Doctor {user.username} has been blacklisted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/blacklist/patient/<int:patient_id>', methods=['POST'])
@jwt_required()
def blacklist_patient(patient_id):
    """Blacklist a patient by patient_id."""
    claims = get_jwt()
    if not check_admin_role(claims):
        return jsonify({'error': 'Unauthorized: Admin only'}), 403

    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404

        user = patient.user
        if not user:
            return jsonify({'error': 'Associated user not found'}), 404

        # Mark user as blacklisted
        user.is_blacklisted = True
        db.session.commit()

        return jsonify({'msg': f'Patient {user.username} has been blacklisted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/blacklist/doctor/<int:doctor_id>', methods=['DELETE'])
@jwt_required()
def unblacklist_doctor(doctor_id):
    """Remove a doctor from blacklist."""
    claims = get_jwt()
    if not check_admin_role(claims):
        return jsonify({'error': 'Unauthorized: Admin only'}), 403

    try:
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404

        user = doctor.user
        if not user:
            return jsonify({'error': 'Associated user not found'}), 404

        user.is_blacklisted = False
        db.session.commit()

        return jsonify({'msg': f'Doctor {user.username} has been unblacklisted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/blacklist/patient/<int:patient_id>', methods=['DELETE'])
@jwt_required()
def unblacklist_patient(patient_id):
    """Remove a patient from blacklist."""
    claims = get_jwt()
    if not check_admin_role(claims):
        return jsonify({'error': 'Unauthorized: Admin only'}), 403

    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404

        user = patient.user
        if not user:
            return jsonify({'error': 'Associated user not found'}), 404

        user.is_blacklisted = False
        db.session.commit()

        return jsonify({'msg': f'Patient {user.username} has been unblacklisted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/blacklist', methods=['POST'])
@jwt_required()
def blacklist_user():
    """Blacklist/disable a user (doctor or patient)."""
    claims = get_jwt()
    if not check_admin_role(claims):
        return jsonify({'error': 'Unauthorized: Admin only'}), 403

    try:
        data = request.get_json()
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        user.is_blacklisted = True
        db.session.commit()

        return jsonify({'msg': f'User {user.username} has been blacklisted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/blacklist/<int:user_id>', methods=['DELETE'])
@jwt_required()
def unblacklist_user(user_id):
    """Remove a user from blacklist."""
    claims = get_jwt()
    if not check_admin_role(claims):
        return jsonify({'error': 'Unauthorized: Admin only'}), 403

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        user.is_blacklisted = False
        db.session.commit()

        return jsonify({'msg': f'User {user.username} has been unblacklisted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================================
# ADMIN DASHBOARD STATS
# ============================================================================

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def dashboard_stats():
    """Get dashboard statistics."""
    claims = get_jwt()
    if not check_admin_role(claims):
        return jsonify({'error': 'Unauthorized: Admin only'}), 403

    try:
        total_patients = Patient.query.count()
        total_doctors = Doctor.query.count()
        total_appointments = Appointment.query.count()

        # Get upcoming appointments
        today = datetime.now().date()
        upcoming = Appointment.query.filter(Appointment.date >= today).count()
        
        # Get completed appointments
        completed = Appointment.query.filter_by(status='Completed').count()

        return jsonify({
            'total_patients': total_patients,
            'total_doctors': total_doctors,
            'total_appointments': total_appointments,
            'upcoming_appointments': upcoming,
            'completed_appointments': completed
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/debug/button', methods=['POST'])
def debug_button():
    data = request.json
    print("\n=== BUTTON CLICKED ===")
    print("Button:", data.get("button"))
    print("Entity ID:", data.get("id"))
    print("=====================\n")
    return {"msg": "Printed"}
