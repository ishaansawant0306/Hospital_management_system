"""
Authentication Routes Module

This module handles all authentication-related endpoints for the Hospital Management System.
It includes user registration, login, and admin dashboard functionality.

Endpoints:
    - POST /register: Register a new patient user
    - POST /login: Authenticate user and return JWT token
    - GET /dashboard: Retrieve admin dashboard statistics (Admin only)
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from models.models import db, User, Patient, Doctor, Appointment
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt


# Create Blueprint for authentication routes
auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # If the client requests the register page, serve the template
    if request.method == 'GET':
        return render_template('register.html')
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
    # Accept either JSON or form-encoded data (helps when form posts from simple HTML page)
    # Use silent=True to avoid raising a BadRequest when Content-Type is not JSON
    data = request.get_json(silent=True) or request.form.to_dict()

    # Required fields
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'msg': 'Email and password are required'}), 400

    # Use email as username if username not provided
    username = data.get('username') or email.split('@')[0]

    # Check if email already exists in database
    if User.query.filter_by(email=email).first():
        return jsonify({'msg': 'Email already registered'}), 400

    # Check if username already exists in database and adjust if necessary
    if User.query.filter_by(username=username).first():
        # append a numeric suffix until unique
        base = username
        i = 1
        while User.query.filter_by(username=f"{base}{i}").first():
            i += 1
        username = f"{base}{i}"

    # Hash the password for security
    hashed_pw = generate_password_hash(password)

    # Create new User record with Patient role
    user = User(username=username, email=email, password=hashed_pw, role='Patient')
    db.session.add(user)
    db.session.commit()

    # Create associated Patient record with additional information
    # Normalize optional patient fields
    contact_info = data.get('contact_info') or data.get('phone') or None
    age = data.get('age') or None
    gender = data.get('gender') or None

    patient = Patient(user_id=user.id, contact_info=contact_info, age=age, gender=gender)
    db.session.add(patient)
    db.session.commit()

    # If the request was a browser form POST, redirect back to the login page
    if request.method == 'POST' and request.form:
        return redirect(url_for('auth_bp.login')) if False else redirect('/')

    return jsonify({'msg': 'Patient registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data.get('email') or not data.get('password'):
            return jsonify({'msg': 'Email and password are required'}), 400

        user = User.query.filter_by(email=data['email']).first()
        if user and check_password_hash(user.password, data['password']):
            if user.is_blacklisted:
                return jsonify({'msg': 'You cannot login. You have been blacklisted'}), 403

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

        # Dummy fallback
        dummy_users = {
            "admin@hospital.com": {"password": "admin123", "role": "Admin"},
            "doctor@hospital.com": {"password": "doc123", "role": "Doctor"},
            "patient@hospital.com": {"password": "pat123", "role": "Patient"}
        }
        email = data.get('email')
        password = data.get('password')
        user = dummy_users.get(email)
        if user and user["password"] == password:
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

        return jsonify({'msg': 'Invalid credentials'}), 401

    except Exception as e:
        import traceback
        traceback.print_exc()  
        return jsonify({'msg': 'Server error', 'error': str(e)}), 500


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