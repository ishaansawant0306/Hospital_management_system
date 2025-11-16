from flask import Flask
from models.models import db
from flask_jwt_extended import JWTManager
from flask_cors import CORS


app = Flask(__name__, static_folder='Static', template_folder='Templates', static_url_path='')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # Replace with env var later
jwt = JWTManager(app)

# Enable CORS with proper settings
CORS(app, supports_credentials=True, allow_headers=['Content-Type', 'Authorization'])

