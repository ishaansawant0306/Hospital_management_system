import os
from app_config import app  # Flask app configured with static and template folders
from routes.auth_routes import auth_bp
from routes.doctor_routes import doctor_bp
from routes.admin_routes import admin_bp
from flask import render_template, send_from_directory, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.models import User, Doctor, Patient, Appointment


# Register API blueprints
app.register_blueprint(doctor_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)


# Debug endpoint to check server status
@app.route('/api/debug/status', methods=['GET'])
def debug_status():
    """Check if backend is running and database is accessible"""
    try:
        total_users = User.query.count()
        total_doctors = Doctor.query.count()
        total_patients = Patient.query.count()
        total_appointments = Appointment.query.count()
        
        return jsonify({
            "status": "Backend is running ✓",
            "database": "Connected ✓",
            "stats": {
                "total_users": total_users,
                "total_doctors": total_doctors,
                "total_patients": total_patients,
                "total_appointments": total_appointments
            }
        }), 200
    except Exception as e:
        return jsonify({
            "status": "Error",
            "error": str(e)
        }), 500


# Debug endpoint to check JWT token info
@app.route('/api/debug/token', methods=['GET'])
@jwt_required()
def debug_token():
    """Check token information"""
    identity = get_jwt_identity()
    claims = get_jwt()
    
    return jsonify({
        "identity": identity,
        "claims": claims,
        "message": "Token is valid ✓"
    }), 200


# Serve index.html at root
@app.route('/')
def index():
    return render_template('index.html')


# Vue router fallback: return index.html for any non-API path so client-side routing works
@app.route('/<path:path>')
def fallback(path):
    # If the path starts with 'api/' or matches a static file, let Flask handle it normally
    if path.startswith('api'):
        return {'error': 'Not Found'}, 404
    # Attempt to serve static files directly (css/js/fonts/favicon etc.)
    try:
        return send_from_directory(app.static_folder, path)
    except Exception:
        return render_template('index.html')


if __name__ == '__main__':
    # Run the unified server on port 8000 for production/single-port dev
    port = int(os.environ.get('PORT', 8000))
    debug_flag = os.environ.get('FLASK_DEBUG', '0') in ('1', 'true', 'True')
    app.run(debug=debug_flag, port=port)