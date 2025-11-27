
from app_config import app
from models.models import User

with app.app_context():
    admins = User.query.filter_by(role='Admin').all()
    for a in admins:
        print(f"Admin: {a.username}, Email: {a.email}")
