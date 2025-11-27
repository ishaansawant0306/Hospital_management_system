
from app_config import app
from flask_jwt_extended import create_access_token
from models.models import User

with app.app_context():
    user = User.query.filter_by(role='Admin').first()
    if user:
        token = create_access_token(identity=str(user.id), additional_claims={'role': user.role})
        print(token)
    else:
        print("No admin user found")
