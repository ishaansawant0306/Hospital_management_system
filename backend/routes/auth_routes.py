"""
Authentication Routes Module

This module handles all authentication-related endpoints for the Hospital Management System.
It includes user registration, login, and admin dashboard functionality.

Endpoints:
    - POST /register: Register a new patient user
    - POST /login: Authenticate user and return JWT token
    - GET /dashboard: Retrieve admin dashboard statistics (Admin only)
"""

from flask import Blueprint, request, jsonify
from models.models import db, User, Patient, Doctor, Appointment
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt


# Create Blueprint for authentication routes
auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new patient user.
    
    Expects JSON payload with:
        - username (str): Unique username
        - email (str): User's email address
        - password (str): Password to be hashed
        - contact_info (str, optional): Patient's contact information
        - age (int, optional): Patient's age
        - gender (str, optional): Patient's gender
    
    Returns:
        - 201: Patient registered successfully
        - 400: Username already exists
    """
    # Extract JSON data from request
    data = request.get_json()
    
    # Check if username already exists in database
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'msg': 'Username already exists'}), 400

    # Hash the password for security
    hashed_pw = generate_password_hash(data['password'])
    
    # Create new User record with Patient role
    user = User(username=data['username'], email=data['email'], password=hashed_pw, role='Patient')
    db.session.add(user)
    db.session.commit()

    # Create associated Patient record with additional information
    patient = Patient(user_id=user.id, contact_info=data.get('contact_info'), age=data.get('age'), gender=data.get('gender'))
    db.session.add(patient)
    db.session.commit()

    return jsonify({'msg': 'Patient registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user with username and password.
    
    Expects JSON payload with:
        - email (str): User's email address
        - password (str): User's password
    
    Returns:
        - 200: Login successful with JWT token and user role
        - 401: Invalid email or password
    """
    # Extract JSON data from request
    data = request.get_json()

    # Validate required fields
    if not data.get('email') or not data.get('password'):
        return jsonify({'msg': 'Email and password are required'}), 400

    # Query database for user with matching email
    user = User.query.filter_by(email=data['email']).first()

    # If user exists and password matches, return a real user token
    if user and check_password_hash(user.password, data['password']):
        token = create_access_token(
            identity=str(user.id),
            additional_claims={'role': user.role, 'username': user.username}
        )
        return jsonify({
            'access_token': token,
            'token_type': 'Bearer',
            'role': user.role,
            'user_id': user.id
        }), 200

    # Fallback: check dummy credentials if real login fails
    dummy_users = {
        "admin@hospital.com": {"password": "admin123", "role": "Admin"},
        "doctor@hospital.com": {"password": "doc123", "role": "Doctor"},
        "patient@hospital.com": {"password": "pat123", "role": "Patient"}
    }

    email = data.get('email')
    password = data.get('password')

    user = dummy_users.get(email)
    if user and user["password"] == password:
        # create a token for dummy user to be consistent with real users
        token = create_access_token(
            identity=f'dummy:{email}',
            additional_claims={'role': user['role'], 'username': email.split('@')[0]}
        )
        return jsonify({
            'access_token': token,
            'token_type': 'Bearer',
            'role': user['role'],
            'user_id': None
        }), 200

    # If neither real nor dummy user matched, return invalid credentials
    return jsonify({'msg': 'Invalid credentials'}), 401


@auth_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def admin_dashboard():
    """
    Retrieve admin dashboard statistics.
    
    Requires:
        - JWT token in Authorization header (format: "Bearer <token>")
        - User role must be 'Admin'
    
    Returns:
        - 200: Dashboard statistics (total patients, doctors, appointments)
        - 403: Unauthorized - User is not an admin
    """
    # Get current user ID from JWT token (the identity we set in create_access_token)
    current_user_id = get_jwt_identity()
    
    # Get additional claims (role, username) from JWT token
    claims = get_jwt()
    current_role = claims.get('role')

    # Check if user has admin role
    if current_role != 'Admin':
        return jsonify({"error": "Unauthorized - Admin access required"}), 403

    # Count total patients in database
    total_patients = Patient.query.count()
    
    # Count total doctors in database
    total_doctors = Doctor.query.count()
    
    # Count total appointments in database
    total_appointments = Appointment.query.count()

    # Return dashboard statistics
    return jsonify({
        "patients": total_patients,
        "doctors": total_doctors,
        "appointments": total_appointments
    }), 200