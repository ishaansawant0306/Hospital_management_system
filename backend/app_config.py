from flask import Flask
from models.models import db
from flask_jwt_extended import JWTManager
from flask_cors import CORS


app = Flask(__name__, static_folder='Static', template_folder='Templates', static_url_path='')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Celery Configuration (using new-style config keys for Celery 5.x+)
app.config['broker_url'] = 'redis://localhost:6379/0'
app.config['result_backend'] = 'redis://localhost:6379/0'

# Initialize Celery
from celery import Celery
from celery.schedules import crontab  # Not needed for interval-based scheduling

celery = Celery(app.name, broker=app.config['broker_url'])
celery.conf.update(app.config)

# Ensure tasks run in app context
class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask

# Celery Beat Schedule
# Using simple intervals instead of crontab for better Windows compatibility
app.config['beat_schedule'] = {
    'daily-reminders': {
        'task': 'tasks.send_daily_reminders',
        'schedule': 60.0,  # TESTING: Run every 60 seconds
        # For production, use: 'schedule': crontab(hour=8, minute=0)
    },
    'monthly-reports': {
        'task': 'tasks.send_monthly_report',
        'schedule': 120.0,  # TESTING: Run every 120 seconds
        # For production, use: 'schedule': crontab(day_of_month=1, hour=9, minute=0)
    },
}

# Ensure Celery Beat uses the schedule
celery.conf.beat_schedule = app.config['beat_schedule']

# Initialize Caching
from flask_caching import Cache
app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # 5 minutes
cache = Cache(app)

db.init_app(app)

app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # Replace with env var later
jwt = JWTManager(app)

# Enable CORS with proper settings
CORS(app, supports_credentials=True, allow_headers=['Content-Type', 'Authorization'])

