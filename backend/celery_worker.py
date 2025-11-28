import eventlet
eventlet.monkey_patch()
from app_config import app, celery
import tasks  # Import tasks to ensure they are registered with Celery

if __name__ == '__main__':
    app.app_context().push()
