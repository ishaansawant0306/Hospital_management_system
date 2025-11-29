"""
Patient Routes Module
Handles all patient-specific functionality including:
- Dashboard data retrieval
- Department and doctor browsing
- Appointment booking and cancellation
- Medical history access
- Doctor search functionality
- Profile management

This module implements the patient-facing API endpoints that allow
patients to interact with the hospital management system.
"""

# Flask imports for handling HTTP requests and responses
from flask import Blueprint, request, jsonify

# JWT authentication imports for securing endpoints
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

# SQLAlchemy utilities for complex database queries
from sqlalchemy import or_  # Used for OR conditions in queries

# Database models
from models.models import db, User, Doctor, Patient, Appointment, Treatment

# JSON handling for parsing treatment notes
import json

# Create Blueprint for patient routes
# All routes in this file will be prefixed with '/patient'
patient_bp = Blueprint('patient_bp', __name__, url_prefix='/patient')


# ========== HELPER FUNCTIONS ==========

def _parse_treatment_notes(notes):
    """
    Safely parse treatment notes from JSON string
    
    Treatment notes are stored as JSON strings in the database.
    This helper function safely parses them and returns a structured dict.
    If parsing fails, returns default empty structure.
    
    Args:
        notes (str or dict): JSON string or dict containing treatment notes
    
    Returns:
        dict: Structured treatment notes with visitType, testDone, medicines, notes
    """
    # Define default structure for treatment notes
    # This ensures we always return consistent data structure
    default_payload = {
        'visitType': '',  # Type of visit (checkup, emergency, etc.)
        'testDone': '',  # Medical tests performed
        'medicines': [],  # List of prescribed medicines
        'notes': ''  # Additional doctor's notes
    }

    # If notes is None or empty, return default
    if not notes:
        return default_payload

    try:
        # Handle both string and dict inputs
        # Sometimes notes might already be parsed
        if isinstance(notes, str):
            parsed = json.loads(notes)
        else:
            parsed = notes

        # Extract fields with fallback to defaults
        return {
            'visitType': parsed.get('visitType', ''),
            'testDone': parsed.get('testDone', ''),
            'medicines': parsed.get('medicines', []),
            'notes': parsed.get('notes', '')
        }
    except (json.JSONDecodeError, TypeError, AttributeError):
        # If JSON parsing fails, return default structure
        # This prevents crashes from malformed data
        return default_payload


# ========== PATIENT DASHBOARD ENDPOINT ==========

@patient_bp.route('/dashboard', methods=['GET'])
@jwt_required()  # Requires valid JWT token
def get_patient_dashboard():
    """
    Get patient dashboard data
    
    Returns basic patient profile information including:
    - Full name and first name
    - Age, gender, contact info
    - Patient ID for further queries
    
    This is typically the first API call made when patient logs in.
    
    Returns:
        200: Patient profile data
        403: Unauthorized (not a patient)
        404: Patient profile not found
        500: Server error
    """
    try:
        # Extract JWT claims to verify user identity and role
        claims = get_jwt()
        current_user_id = get_jwt_identity()
        current_role = claims.get('role')

        # Authorization check: Only patients can access this endpoint
        if current_role != 'Patient':
            return jsonify({'error': 'Unauthorized: Patient access required'}), 403

        # Fetch patient record from database
        # Patient table is linked to User table via user_id foreign key
        patient = Patient.query.filter_by(user_id=current_user_id).first()
        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404

        # Extract and format first name for personalized greeting
        # Usernames might contain underscores or spaces
        username = patient.user.username if patient.user else ''
        
        # Handle both underscore-separated and space-separated names
        if '_' in username:
            first_name = username.split('_')[0]
        elif username:
            first_name = username.split()[0]
        else:
            first_name = 'Patient'  # Fallback if username is empty
        
        # Capitalize first letter for proper display
        first_name = first_name.capitalize()

        # Return patient profile data
        return jsonify({
            'patient': {
                'id': patient.id,
                'name': patient.user.username if patient.user else None,
                'first_name': first_name,  # Used for "Welcome, [Name]" message
                'age': patient.age,
                'gender': patient.gender,
                'contact_info': patient.contact_info
            }
        }), 200
        
    except Exception as e:
        # Catch any unexpected errors and log them
        print(f"Error in get_patient_dashboard: {str(e)}")
        import traceback
        traceback.print_exc()  # Print full stack trace for debugging
        return jsonify({'error': f'Server error: {str(e)}'}), 500


# ========== DEPARTMENTS LISTING ENDPOINT ==========

@patient_bp.route('/departments', methods=['GET'])
@jwt_required()
def get_departments():
    """
    Get all available departments/specializations
    
    Dynamically generates list of departments based on doctor specializations
    in the database. Only includes specializations that have at least one
    non-blacklisted doctor.
    
    This approach ensures departments are always up-to-date with available doctors.
    
    Returns:
        200: List of departments with id, name, and key
        403: Unauthorized
        500: Server error
    """
    try:
        # Verify user is a patient
        claims = get_jwt()
        current_role = claims.get('role')

        if current_role != 'Patient':
            return jsonify({'error': 'Unauthorized: Patient access required'}), 403

        # Query database for unique specializations
        # Join with User table to filter out blacklisted doctors
        # Use distinct() to get only unique specializations
        specializations = db.session.query(Doctor.specialization).distinct()\
            .join(User, Doctor.user_id == User.id)\
            .filter(User.is_blacklisted == False)\
            .all()
        
        # Build departments list with proper formatting
        departments = []
        for idx, (spec,) in enumerate(specializations, start=1):
            # Only include non-null specializations
            if spec:
                departments.append({
                    'id': idx,  # Sequential ID for frontend
                    'name': spec.title(),  # Capitalize for display
                    'key': spec.lower()  # Lowercase key for URL routing
                })
        
        # Sort departments alphabetically for better UX
        departments.sort(key=lambda x: x['name'])
        
        return jsonify({'departments': departments}), 200
        
    except Exception as e:
        # Log error and return user-friendly message
        print(f"Error in get_departments: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


# ========== DOCTORS BY DEPARTMENT ENDPOINT ==========

# Import caching utility for performance optimization
from app_config import cache

@patient_bp.route('/departments/<department_name>/doctors', methods=['GET'])
@jwt_required()
# Note: Caching removed for real-time updates during development
# In production, consider adding: @cache.cached(timeout=300)
def get_doctors_by_department(department_name):
    """
    Get all doctors for a specific department
    
    Performs case-insensitive search for doctors by specialization.
    Includes department name mapping to handle variations
    (e.g., "cardiology" matches "cardiologist").
    
    Args:
        department_name (str): Department name from URL path
    
    Returns:
        200: List of doctors in the department
        403: Unauthorized
        500: Server error
    """
    try:
        # Verify patient authorization
        claims = get_jwt()
        current_role = claims.get('role')

        if current_role != 'Patient':
            return jsonify({'error': 'Unauthorized: Patient access required'}), 403

        # Department name mapping for flexible matching
        # This allows matching different variations of the same specialization
        # For example, "cardiology" should match both "Cardiology" and "Cardiologist"
        department_mapping = {
            'cardiology': ['cardiology', 'cardiologist'],
            'oncology': ['oncology', 'oncologist'],
            'general': ['general', 'internal medicine', 'general medicine']
        }

        # Get search terms for this department
        # Default to the department name itself if no mapping exists
        search_terms = department_mapping.get(department_name.lower(), [department_name.lower()])
        
        # Build SQL query filters for case-insensitive partial matching
        # Use ilike for case-insensitive LIKE queries (works in PostgreSQL and SQLite)
        filters = []
        for term in search_terms:
            # %term% allows matching anywhere in the specialization string
            filters.append(Doctor.specialization.ilike(f'%{term}%'))
        
        # Execute query with OR condition (match any of the search terms)
        if filters:
            doctors = Doctor.query.filter(or_(*filters)).all()
        else:
            doctors = []
        
        # Debug logging to track search results
        print(f"Searching for department '{department_name}' with terms: {search_terms}")
        print(f"Found {len(doctors)} doctors")
        for doc in doctors:
            print(f"  - {doc.user.username if doc.user else 'N/A'}: {doc.specialization}")

        # Build response list with formatted doctor information
        doctors_list = []
        for doctor in doctors:
            # Filter out blacklisted doctors
            if doctor.user and not doctor.user.is_blacklisted:
                # Format doctor name with "Dr." prefix
                # Replace underscores with spaces and capitalize
                username = doctor.user.username.replace('_', ' ').title()
                
                # Remove existing "Dr." prefix if present to avoid duplication
                if username.lower().startswith('dr.'):
                    username = username[3:].strip()
                
                # Add "Dr." prefix for professional display
                doctor_name = f"Dr. {username}"
                
                doctors_list.append({
                    'id': doctor.id,
                    'name': doctor_name,
                    'specialization': doctor.specialization,
                    'doctor_id': doctor.doctor_id  # Unique doctor identifier
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
