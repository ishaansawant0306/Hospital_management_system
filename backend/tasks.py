from app_config import celery
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

# --- Google Chat Webhook Function ---
def send_google_chat_webhook(message):
    # TODO: User needs to replace this with their actual Webhook URL
    webhook_url = "https://chat.googleapis.com/v1/spaces/AAQAKWT9nwc/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=16FaJbM9Lw6leBMz3fILRh4HtY2ZNbinS7T4VLLLQR8" 
    
    if webhook_url == "YOUR_GOOGLE_CHAT_WEBHOOK_URL_HERE":
        print("No Webhook URL configured. Skipping Google Chat notification.")
        return

    try:
        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        data = {'text': message}
        response = requests.post(webhook_url, headers=headers, data=json.dumps(data))
        print(f"Google Chat Webhook Response: {response.status_code}")
    except Exception as e:
        print(f"Error sending to Google Chat: {e}")

# --- Mock Email Function (Replace with real SMTP later) ---
def send_email(to_email, subject, body, is_html=False):
    print(f"--------------------------------------------------")
    print(f"MOCK EMAIL TO: {to_email}")
    print(f"SUBJECT: {subject}")
    print(f"BODY: {body[:100]}...") # Print first 100 chars
    print(f"--------------------------------------------------")
    # In production, use smtplib here
    # msg = MIMEMultipart()
    # ...

@celery.task
def send_daily_reminders():
    """
    Daily task to check for appointments scheduled for today and send reminders.
    """
    print("Starting daily reminder task...")
    today = datetime.now().date()
    
    # Find appointments for today
    # Note: We need to be inside app context, which Celery handles if configured correctly
    appointments = Appointment.query.filter_by(date=today).all()
    
    print(f"DEBUG: Checking for appointments on {today}")
    print(f"DEBUG: Found {len(appointments)} appointments.")
    for a in appointments:
        print(f"DEBUG: Appointment ID: {a.id}, Date: {a.date}, Status: {a.status}")
    
    for appt in appointments:
        patient = Patient.query.get(appt.patient_id)
        user = User.query.get(patient.user_id)
        doctor = Doctor.query.get(appt.doctor_id)
        doctor_user = User.query.get(doctor.user_id)
        
        # Format names
        patient_name = user.username.replace('_', ' ').title()
        doctor_name = doctor_user.username.replace('_', ' ').title()
        
        subject = f"Appointment Reminder: {today}"
        body = f"Hello {patient_name},\n\nYou have an appointment today with Dr. {doctor_name} at {appt.time}.\nPlease arrive on time."
        
        send_email(user.email, subject, body)
        
        # Send to Google Chat as well
        chat_message = f"🔔 *Daily Reminder*\nHi {patient_name}, don't forget your appointment with Dr. {doctor_name} today at {appt.time}!"
        send_google_chat_webhook(chat_message)
    
    return f"Sent reminders for {len(appointments)} appointments."

@celery.task
def send_monthly_report():
    """
    Monthly task to generate activity report for doctors.
    """
    print("Starting monthly report task...")
    # Logic to generate HTML report
    # For now, we will mock this
    doctors = Doctor.query.all()
    
    for doctor in doctors:
        user = User.query.get(doctor.user_id)
        # Generate report data (mock)
        appointments_count = len(doctor.appointments)
        
        # Format name
        doctor_name = user.username.replace('_', ' ').title()
        
        subject = "Monthly Activity Report"
        body = f"<h1>Monthly Report</h1><p>Dr. {doctor_name}, you had {appointments_count} appointments this month.</p>"
        
        send_email(user.email, subject, body, is_html=True)
        
    return "Monthly reports sent."

@celery.task
def export_patient_treatments(user_id):
    """
    Async task to export patient treatments to CSV.
    """
    print(f"Starting CSV export for user_id: {user_id}...")
    user = User.query.get(user_id)
    if not user or user.role != 'Patient':
        return "Invalid user"
        
    patient = user.patient
    appointments = Appointment.query.filter_by(patient_id=patient.id).all()
    
    safe_username = user.username.replace(" ", "_")
    filename = f"treatments_{safe_username}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    filepath = os.path.join('static', 'exports', filename)
    
    # Ensure directory exists
    os.makedirs(os.path.join('static', 'exports'), exist_ok=True)
    
    with open(filepath, 'w', newline='') as csvfile:
        fieldnames = ['Date', 'Doctor', 'Diagnosis', 'Prescription', 'Notes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for appt in appointments:
            doctor = Doctor.query.get(appt.doctor_id)
            doctor_user = User.query.get(doctor.user_id)
            treatment = appt.treatment
            
            writer.writerow({
                'Date': appt.date,
                'Doctor': doctor_user.username,
                'Diagnosis': treatment.diagnosis if treatment else 'N/A',
                'Prescription': treatment.prescription if treatment else 'N/A',
                'Notes': treatment.notes if treatment else 'N/A'
            })
            
    # Send alert/email that export is ready
    subject = "Export Ready"
    body = f"Your treatment history has been exported. Download it here: {filename}" # In real app, provide full URL
    send_email(user.email, subject, body)
    
    # Send to Google Chat
    download_link = f"http://localhost:5000/exports/{filename}"
    formatted_name = user.username.replace('_', ' ').title()
    send_google_chat_webhook(f"📂 *Export Complete*\nHi {formatted_name}, your treatment history is ready!\nDownload here: {download_link}")
    
    return f"Export generated: {filepath}"
