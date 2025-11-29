"""
Authentication Routes
Handles user registration, login, and dashboard access
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from models.models import db, User, Patient, Doctor, Appointment
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt


# Create Blueprint for authentication routes
# Blueprint helps organize related routes together
# All routes in this file will be prefixed with /api (configured in main.py)
auth_bp = Blueprint('auth_bp', __name__)


# ========== PATIENT REGISTRATION ENDPOINT ==========
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Register a new patient user
    
    Handles both GET (serve registration page) and POST (process registration)
    
    POST expects JSON with:
        - email (required): User's email address
        - password (required): User's password (will be hashed)
        - username (optional): Display name (defaults to email prefix)
        - contact_info (optional): Phone number or contact details
        - age (optional): Patient's age
        - gender (optional): Patient's gender
    
    Returns:
        - 201: Patient registered successfully
        - 400: Missing required fields or email already exists
    """
    
    # If GET request, serve the registration HTML page
    if request.method == 'GET':
        return render_template('register.html')
    
    # Handle POST request (registration submission)
    # Accept both JSON and form-encoded data
    # silent=True prevents error when Content-Type is not application/json
    data = request.get_json(silent=True) or request.form.to_dict()

    # Extract and validate required fields
    email = data.get('email')
    password = data.get('password')
    
    # Check if required fields are present
    if not email or not password:
        return jsonify({'msg': 'Email and password are required'}), 400

    # Generate username from email if not provided
    # Example: "john@example.com" becomes "john"
    username = data.get('username') or email.split('@')[0]

    # Check if email already exists in database
    # This prevents duplicate accounts
    if User.query.filter_by(email=email).first():
        return jsonify({'msg': 'Email already registered'}), 400

    # Check if username is already taken
    # If taken, append a number to make it unique
    if User.query.filter_by(username=username).first():
        base = username
        i = 1
        # Keep incrementing until we find an available username
        while User.query.filter_by(username=f"{base}{i}").first():
            i += 1
        username = f"{base}{i}"

    # Hash the password for security
    # Never store plain text passwords in database!
    # Werkzeug uses pbkdf2:sha256 by default
    hashed_pw = generate_password_hash(password)

    # Create new User record
    # All patients have role='Patient'
    user = User(username=username, email=email, password=hashed_pw, role='Patient')
    db.session.add(user)
    db.session.commit()  # Commit to get user.id

    # Create associated Patient profile
    # Extract optional patient-specific fields
    # Use 'or' operator to handle missing fields gracefully
    contact_info = data.get('contact_info') or data.get('phone') or None
    age = data.get('age') or None
    gender = data.get('gender') or None

    # Create Patient record linked to User
    patient = Patient(user_id=user.id, contact_info=contact_info, age=age, gender=gender)
    db.session.add(patient)
    db.session.commit()

    # If request came from HTML form, redirect to login page
    # Otherwise, return JSON response (for API clients)
    if request.method == 'POST' and request.form:
        return redirect(url_for('auth_bp.login')) if False else redirect('/')

    return jsonify({'msg': 'Patient registered successfully'}), 201


# ========== LOGIN ENDPOINT ==========
@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and return JWT token
    
    Expects JSON with:
        - email (str): User's email address
        - password (str): User's password
    
    Returns:
        - 200: Login successful with JWT token
        - 400: Missing email or password
        - 401: Invalid credentials
        - 403: User is blacklisted
        - 500: Server error
    """
    try:
        # Parse JSON request body
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'msg': 'Email and password are required'}), 400

        # Look up user by email
        user = User.query.filter_by(email=data['email']).first()
        
        # Verify user exists and password is correct
        if user and check_password_hash(user.password, data['password']):
            # Check if user is blacklisted
            # Blacklisted users cannot login
            if user.is_blacklisted:
                return jsonify({'msg': 'You cannot login. You have been blacklisted'}), 403

            # Create JWT access token
            # identity: unique user identifier (user ID as string)
            # additional_claims: extra data stored in token (role, username)
            token = create_access_token(
                identity=str(user.id),
                additional_claims={'role': user.role, 'username': user.username}
            )
            
            # Return token and user information
            return jsonify({
                'access_token': token,
                'token_type': 'Bearer',  # Standard token type for Authorization header
                'role': user.role,  # Used by frontend to determine which dashboard to show
                'user_id': user.id
            }), 200

        # ========== FALLBACK: DUMMY USERS FOR TESTING ==========
        # This section provides hardcoded test accounts
        # Useful for development when database is empty
        # TODO: Remove this in production!
        dummy_users = {
            "admin@hospital.com": {"password": "admin123", "role": "Admin"},
            "doctor@hospital.com": {"password": "doc123", "role": "Doctor"},
            "patient@hospital.com": {"password": "pat123", "role": "Patient"}
        }
        
        email = data.get('email')
        password = data.get('password')
        user = dummy_users.get(email)
        
        # Check if credentials match dummy user
        if user and user["password"] == password:
            # Create token for dummy user
            token = create_access_token(
                identity=f'dummy:{email}',  # Special identity format for dummy users
                additional_claims={'role': user['role'], 'username': email.split('@')[0]}
            )
            return jsonify({
                'access_token': token,
                'token_type': 'Bearer',
                'role': user['role'],
                'user_id': None  # Dummy users don't have database IDs
            }), 200

        # If we reach here, credentials are invalid
        return jsonify({'msg': 'Invalid credentials'}), 401

    except Exception as e:
        # Catch any unexpected errors
        import traceback
        traceback.print_exc()  # Print full error trace for debugging
        return jsonify({'msg': 'Server error', 'error': str(e)}), 500


# ========== ADMIN DASHBOARD ENDPOINT ==========
@auth_bp.route('/dashboard', methods=['GET'])
@jwt_required()  # Requires valid JWT token in Authorization header
def admin_dashboard():
    """
    Get admin dashboard statistics
    
    This endpoint is protected - requires JWT token with Admin role.
    Returns counts of patients, doctors, and appointments.
    
    Headers required:
        Authorization: Bearer <jwt_token>
    
    Returns:
        - 200: Dashboard statistics
        - 403: Unauthorized (not an admin)
    """
    
    # Extract user ID from JWT token
    # This is the 'identity' we set when creating the token
    current_user_id = get_jwt_identity()
    
    # Get additional claims from JWT token
    # Claims include role, username, etc.
    claims = get_jwt()
    current_role = claims.get('role')

    # Verify user has admin role
    # Only admins can access dashboard statistics
    if current_role != 'Admin':
        return jsonify({"error": "Unauthorized - Admin access required"}), 403

    # Query database for statistics
    # Count total records in each table
    total_patients = Patient.query.count()
    total_doctors = Doctor.query.count()
    total_appointments = Appointment.query.count()

    # Return statistics as JSON
    return jsonify({
        "patients": total_patients,
        "doctors": total_doctors,
        "appointments": total_appointments
    }), 200