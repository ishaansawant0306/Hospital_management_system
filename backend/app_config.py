from flask import Flask
from models.models import db
from flask_jwt_extended import JWTManager


app = Flask(__name__, static_folder='Static', template_folder='Templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # Replace with env var later
jwt = JWTManager(app)

