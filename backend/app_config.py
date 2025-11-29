"""
Flask Application Configuration
Sets up Flask app, database, JWT, Celery, and caching
"""

from flask import Flask
from models.models import db
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from celery import Celery
from flask_caching import Cache
import os

# ========== Flask App Setup ==========
app = Flask(
    __name__,
    static_folder='Static',
    template_folder='Templates',
    static_url_path=''
)

# ========== Database Configuration ==========
DB_PATH = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_DATABASE_URI'] = DB_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# ========== JWT Configuration ==========
# TODO: Move secret key to environment variable for production
JWT_SECRET = os.environ.get('JWT_SECRET', 'super-secret-key')
app.config['JWT_SECRET_KEY'] = JWT_SECRET
jwt = JWTManager(app)

# ========== CORS Setup ==========
# Allow cross-origin requests with credentials
CORS(
    app,
    supports_credentials=True,
    allow_headers=['Content-Type', 'Authorization']
)

# ========== Redis & Celery Configuration ==========
REDIS_URL = 'redis://localhost:6379/0'
app.config['broker_url'] = REDIS_URL
app.config['result_backend'] = REDIS_URL

# Create Celery instance
celery = Celery(app.name, broker=app.config['broker_url'])
celery.conf.update(app.config)

# Custom task class to ensure Flask app context
class FlaskContextTask(celery.Task):
    """Wraps Celery tasks to run within Flask app context"""
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = FlaskContextTask

# ========== Celery Beat Scheduler ==========
# Define periodic tasks schedule
# NOTE: Using intervals for testing; switch to crontab for production
BEAT_SCHEDULE = {
    'send-daily-appointment-reminders': {
        'task': 'tasks.send_daily_reminders',
        'schedule': 60.0,  # Every 60 seconds (testing mode)
        # Production: 'schedule': crontab(hour=8, minute=0)
    },
    'generate-monthly-reports': {
        'task': 'tasks.send_monthly_report',
        'schedule': 120.0,  # Every 120 seconds (testing mode)
        # Production: 'schedule': crontab(day_of_month=1, hour=9, minute=0)
    },
}

app.config['beat_schedule'] = BEAT_SCHEDULE
celery.conf.beat_schedule = BEAT_SCHEDULE

# ========== Caching Configuration ==========
app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_URL'] = REDIS_URL
app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # Cache timeout: 5 minutes

cache = Cache(app)
