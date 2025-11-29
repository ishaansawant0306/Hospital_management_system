"""
Main Application Entry Point
This is the central file that starts the Flask server and registers all routes.
It handles both API endpoints and serves the Vue.js frontend.
"""

import os
from app_config import app  # Import the configured Flask app instance
from routes.auth_routes import auth_bp  # Authentication routes (login, register)
from routes.doctor_routes import doctor_bp  # Doctor-specific routes
from routes.admin_routes import admin_bp  # Admin management routes
from routes.patient_routes import patient_bp  # Patient-specific routes
from flask import render_template, send_from_directory, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.models import User, Doctor, Patient, Appointment


# ========== REGISTER ALL BLUEPRINTS ==========
# Blueprints help organize routes into separate modules
# Each blueprint handles a specific part of the application
app.register_blueprint(doctor_bp)  # Routes under /api/doctor
app.register_blueprint(auth_bp)  # Routes under /api/auth (login, register)
app.register_blueprint(admin_bp)  # Routes under /api/admin
app.register_blueprint(patient_bp)  # Routes under /api/patient


# ========== DEBUG ENDPOINTS ==========
# These endpoints help verify the backend is working correctly
# Useful during development and testing

@app.route('/api/debug/status', methods=['GET'])
def debug_status():
    """
    Health check endpoint - verifies backend and database connectivity
    Returns current database statistics
    """
    try:
        # Query database to count records in each table
        # This also verifies that database connection is working
        total_users = User.query.count()
        total_doctors = Doctor.query.count()
        total_patients = Patient.query.count()
        total_appointments = Appointment.query.count()
        
        # Return success response with statistics
        return jsonify({
            "status": "Backend is running",
            "database": "Connected",
            "stats": {
                "total_users": total_users,
                "total_doctors": total_doctors,
                "total_patients": total_patients,
                "total_appointments": total_appointments
            }
        }), 200
    except Exception as e:
        # If database query fails, return error
        return jsonify({
            "status": "Error",
            "error": str(e)
        }), 500


@app.route('/api/debug/token', methods=['GET'])
@jwt_required()  # This endpoint requires valid JWT token
def debug_token():
    """
    Token verification endpoint - checks if JWT token is valid
    Useful for debugging authentication issues
    """
    # Extract user identity from JWT token
    identity = get_jwt_identity()
    
    # Get additional claims (role, username, etc.) from token
    claims = get_jwt()
    
    # Return token information
    return jsonify({
        "identity": identity,
        "claims": claims,
        "message": "Token is valid"
    }), 200


# ========== FRONTEND SERVING ==========
# These routes handle serving the Vue.js single-page application

@app.route('/')
def index():
    """
    Serve the main index.html page
    This is the entry point for the Vue.js frontend
    """
    return render_template('index.html')


@app.route('/<path:path>')
def fallback(path):
    """
    Fallback route for Vue Router (client-side routing)
    
    Vue Router handles navigation on the frontend, but when users refresh
    the page or directly visit a URL, the server needs to return index.html
    so Vue Router can take over.
    
    This function:
    1. Returns 404 for API routes (they should be handled by blueprints)
    2. Tries to serve static files (CSS, JS, images)
    3. Falls back to index.html for all other routes (Vue Router handles them)
    """
    
    # If path starts with 'api', it's an API call that wasn't found
    if path.startswith('api'):
        return {'error': 'Not Found'}, 404
    
    # Try to serve static files (CSS, JS, images, fonts, etc.)
    try:
        return send_from_directory(app.static_folder, path)
    except Exception:
        # If file not found, return index.html
        # This allows Vue Router to handle the route on the client side
        return render_template('index.html')


# ========== APPLICATION STARTUP ==========
if __name__ == '__main__':
    """
    Start the Flask development server
    This block only runs when the file is executed directly (not imported)
    """
    
    # Get port from environment variable, default to 5000
    # This allows easy port configuration without changing code
    port = int(os.environ.get('PORT', 5000))
    
    # Check if debug mode should be enabled
    # Debug mode provides better error messages and auto-reloads on code changes
    # IMPORTANT: Never use debug=True in production!
    debug_flag = os.environ.get('FLASK_DEBUG', '0') in ('1', 'true', 'True')
    
    # Print startup information
    print(f"\n=== Hospital Management System ===")
    print(f"Starting Flask server on http://127.0.0.1:{port}")
    print(f"Debug mode: {debug_flag}\n")
    
    # Start the Flask development server
    # host='127.0.0.1' means only accessible from localhost (secure for development)
    app.run(debug=debug_flag, port=port, host='127.0.0.1')