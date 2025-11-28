"""
Test script to manually trigger the Celery tasks to verify they work.
This bypasses the scheduler and directly calls the task functions.
"""
import eventlet
eventlet.monkey_patch()

from app_config import app
from tasks import send_daily_reminders, send_monthly_report

if __name__ == '__main__':
    with app.app_context():
        print("\n=== Testing Daily Reminders ===")
        result = send_daily_reminders()
        print(f"Result: {result}")
        
        print("\n=== Testing Monthly Report ===")
        result = send_monthly_report()
        print(f"Result: {result}")
        
        print("\n=== All tests complete ===")
