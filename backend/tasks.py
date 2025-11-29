"""
Celery Background Tasks
This file contains all asynchronous tasks that run in the background.
Tasks include sending reminders, generating reports, and exporting data.
"""

from app_config import celery  # Import Celery instance configured in app_config
from models.models import User, Appointment, Treatment, Patient, Doctor
from flask import render_template
import csv
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json


# ========== GOOGLE CHAT WEBHOOK INTEGRATION ==========
def send_google_chat_webhook(message):
    """
    Send notification to Google Chat using webhook
    
    This function posts messages to a Google Chat space.
    Useful for real-time notifications about appointments and system events.
    
    Args:
        message (str): The message text to send
    """
    # NOTE: Replace this URL with your actual Google Chat webhook URL
    # You can create a webhook in Google Chat: Space settings > Apps & integrations > Webhooks
    webhook_url = "https://chat.googleapis.com/v1/spaces/AAQAKWT9nwc/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=16FaJbM9Lw6leBMz3fILRh4HtY2ZNbinS7T4VLLLQR8"
    
    # Check if webhook URL is configured
    if webhook_url == "YOUR_GOOGLE_CHAT_WEBHOOK_URL_HERE":
        print("No Webhook URL configured. Skipping Google Chat notification.")
        return

    try:
        # Prepare HTTP request headers
        # Google Chat expects JSON content type with UTF-8 encoding
        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        
        # Create message payload
        # Google Chat webhook accepts simple text messages in this format
        data = {'text': message}
        
        # Send POST request to webhook URL
        response = requests.post(webhook_url, headers=headers, data=json.dumps(data))
        
        # Log response status for debugging
        print(f"Google Chat Webhook Response: {response.status_code}")
    except Exception as e:
        # Catch any errors (network issues, invalid URL, etc.)
        print(f"Error sending to Google Chat: {e}")


# ========== EMAIL SENDING FUNCTION ==========
def send_email(to_email, subject, body, is_html=False):
    """
    Send email to user (currently mocked for testing)
    
    In production, this would use SMTP to send real emails.
    For now, it just prints the email content to console.
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject line
        body (str): Email body content
        is_html (bool): Whether body contains HTML (default: False)
    
    TODO: Implement real SMTP email sending for production
    TODO: Add email templates for better formatting
    """
    # Print mock email to console
    print(f"--------------------------------------------------")
    print(f"MOCK EMAIL TO: {to_email}")
    print(f"SUBJECT: {subject}")
    print(f"BODY: {body[:100]}...")  # Print first 100 characters only
    print(f"--------------------------------------------------")
    
    # Production implementation would look like this:
    # msg = MIMEMultipart()
    # msg['From'] = 'hospital@example.com'
    # msg['To'] = to_email
    # msg['Subject'] = subject
    # msg.attach(MIMEText(body, 'html' if is_html else 'plain'))
    # 
    # with smtplib.SMTP('smtp.gmail.com', 587) as server:
    #     server.starttls()
    #     server.login('your_email@gmail.com', 'your_password')
    #     server.send_message(msg)


# ========== CELERY TASK: DAILY APPOINTMENT REMINDERS ==========
@celery.task
def send_daily_reminders():
    """
    Scheduled task to send appointment reminders
    
    This task runs daily (configured in app_config.py) and:
    1. Finds all appointments scheduled for today
    2. Sends reminder emails to patients
    3. Posts notifications to Google Chat
    
    Returns:
        str: Summary message indicating how many reminders were sent
    """
    print("Starting daily reminder task...")
    
    # Get today's date (without time component)
    today = datetime.now().date()
    
    # Query database for all appointments scheduled for today
    # NOTE: Celery tasks run in Flask app context (configured in app_config.py)
    # FIX: Only select 'Booked' appointments to avoid reminders for completed/cancelled ones
    appointments = Appointment.query.filter_by(date=today, status='Booked').all()
    
    # Debug logging to track task execution
    print(f"DEBUG: Checking for appointments on {today}")
    print(f"DEBUG: Found {len(appointments)} appointments.")
    
    # Log each appointment for debugging
    for a in appointments:
        print(f"DEBUG: Appointment ID: {a.id}, Date: {a.date}, Status: {a.status}")
    
    # Process each appointment
    for appt in appointments:
        # Fetch related patient, user, and doctor information
        # We need to join multiple tables to get all required data
        patient = Patient.query.get(appt.patient_id)
        user = User.query.get(patient.user_id)  # Patient's user account
        doctor = Doctor.query.get(appt.doctor_id)
        doctor_user = User.query.get(doctor.user_id)  # Doctor's user account
        
        # Format names for display
        # Replace underscores with spaces and capitalize each word
        patient_name = user.username.replace('_', ' ').title()
        doctor_name = doctor_user.username.replace('_', ' ').title()
        
        # Compose email content
        subject = f"Appointment Reminder: {today}"
        body = f"Hello {patient_name},\n\nYou have an appointment today with Dr. {doctor_name} at {appt.time}.\nPlease arrive on time."
        
        # Send email reminder
        send_email(user.email, subject, body)
        
        # Also send notification to Google Chat
        chat_message = f"🔔 *Daily Reminder*\nHi {patient_name}, don't forget your appointment with Dr. {doctor_name} today at {appt.time}!"
        send_google_chat_webhook(chat_message)
    
    # Return summary of task execution
    return f"Sent reminders for {len(appointments)} appointments."


# ========== CELERY TASK: MONTHLY ACTIVITY REPORTS ==========
@celery.task
def send_monthly_report():
    """
    Scheduled task to generate and send monthly activity reports
    
    This task runs monthly (configured in app_config.py) and:
    1. Generates activity reports for each doctor
    2. Includes statistics like total appointments
    3. Sends HTML-formatted email reports
    
    Returns:
        str: Confirmation message
    """
    print("Starting monthly report task...")
    
    # Get all doctors from database
    doctors = Doctor.query.all()
    
    # Generate and send report for each doctor
    for doctor in doctors:
        # Get doctor's user account for email address
        user = User.query.get(doctor.user_id)
        
        # Calculate statistics
        # Count total appointments for this doctor
        appointments_count = len(doctor.appointments)
        
        # Format doctor name for display
        doctor_name = user.username.replace('_', ' ').title()
        
        # Create HTML email content
        subject = "Monthly Activity Report"
        body = f"<h1>Monthly Report</h1><p>Dr. {doctor_name}, you had {appointments_count} appointments this month.</p>"
        
        # Send HTML email
        send_email(user.email, subject, body, is_html=True)
    
    return "Monthly reports sent."


# ========== CELERY TASK: EXPORT PATIENT TREATMENT HISTORY ==========
@celery.task
def export_patient_treatments(user_id):
    """
    Asynchronous task to export patient treatment history to CSV
    
    This task runs in the background when a patient requests their data.
    It generates a CSV file with all appointments and treatments.
    
    Args:
        user_id (int): The user ID of the patient requesting export
    
    Returns:
        str: Path to generated CSV file or error message
    """
    print(f"Starting CSV export for user_id: {user_id}...")
    
    # Fetch user from database
    user = User.query.get(user_id)
    
    # Validate user exists and is a patient
    if not user or user.role != 'Patient':
        return "Invalid user"
    
    # Get patient profile
    patient = user.patient
    
    # Fetch all appointments for this patient
    appointments = Appointment.query.filter_by(patient_id=patient.id).all()
    
    # Generate unique filename
    # Replace spaces with underscores to avoid file system issues
    safe_username = user.username.replace(" ", "_")
    
    # Include timestamp to ensure uniqueness
    filename = f"treatments_{safe_username}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    
    # Define file path (store in static/exports directory)
    filepath = os.path.join('static', 'exports', filename)
    
    # Create exports directory if it doesn't exist
    # exist_ok=True prevents error if directory already exists
    os.makedirs(os.path.join('static', 'exports'), exist_ok=True)
    
    # Write data to CSV file
    with open(filepath, 'w', newline='') as csvfile:
        # Define CSV columns
        fieldnames = ['Date', 'Doctor', 'Diagnosis', 'Prescription', 'Notes']
        
        # Create CSV writer
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header row
        writer.writeheader()
        
        # Write data for each appointment
        for appt in appointments:
            # Get doctor information
            doctor = Doctor.query.get(appt.doctor_id)
            doctor_user = User.query.get(doctor.user_id)
            
            # Get treatment record (if exists)
            treatment = appt.treatment
            
            # Write row to CSV
            writer.writerow({
                'Date': appt.date,
                'Doctor': doctor_user.username,
                'Diagnosis': treatment.diagnosis if treatment else 'N/A',
                'Prescription': treatment.prescription if treatment else 'N/A',
                'Notes': treatment.notes if treatment else 'N/A'
            })
    
    # Notify user that export is ready
    subject = "Export Ready"
    body = f"Your treatment history has been exported. Download it here: {filename}"
    send_email(user.email, subject, body)
    
    # Also send Google Chat notification
    download_link = f"http://localhost:5000/exports/{filename}"
    formatted_name = user.username.replace('_', ' ').title()
    send_google_chat_webhook(f"📂 *Export Complete*\nHi {formatted_name}, your treatment history is ready!\nDownload here: {download_link}")
    
    return f"Export generated: {filepath}"
