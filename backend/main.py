from app_config import app  # ✅ This is your actual Flask app instance
from routes.auth_routes import auth_bp
from routes.doctor_routes import doctor_bp
from flask_cors import CORS
from flask import render_template

# ✅ Apply CORS to the imported app
CORS(app)

# ✅ Serve Vue frontend
@app.route('/')
def index():
    return render_template('index.html')

# ✅ Register blueprints
app.register_blueprint(doctor_bp)
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    app.run(debug=False, port=8000)