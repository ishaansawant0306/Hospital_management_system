"""
Database Models Module

This module defines all SQLAlchemy database models for the Hospital Management System.
It includes models for Users, Doctors, Patients, Appointments, Treatments, and Departments.

Models:
    - User: Base user model with role-based access (Admin, Doctor, Patient)
    - Doctor: Doctor information linked to User model
    - Patient: Patient information linked to User model
    - Appointment: Appointment scheduling between doctors and patients
    - Treatment: Medical treatment records associated with appointments
    - Department: Hospital departments
"""

from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy database instance
db = SQLAlchemy()


class User(db.Model):
    """
    User Model - Represents all users in the system (Admin, Doctor, Patient)
    
    Attributes:
        id (int): Primary key, unique identifier for the user
        username (str): Unique username for login
        email (str): Unique email address
        password (str): Hashed password for security
        role (str): User role ('Admin', 'Doctor', or 'Patient')
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'Admin', 'Doctor', 'Patient'

    # Relationships: One User can have one Doctor or Patient profile
    doctor = db.relationship('Doctor', backref='user', uselist=False)
    patient = db.relationship('Patient', backref='user', uselist=False)


class Doctor(db.Model):
    """
    Doctor Model - Stores doctor-specific information
    
    Attributes:
        id (int): Primary key, unique identifier for the doctor
        user_id (int): Foreign key linking to User model
        specialization (str): Medical specialization (e.g., Cardiology, Neurology)
        availability (str): Doctor's availability schedule
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    availability = db.Column(db.String, nullable=True)

    # Relationship: One Doctor can have multiple Appointments
    appointments = db.relationship('Appointment', backref='doctor')


class Patient(db.Model):
    """
    Patient Model - Stores patient-specific information
    
    Attributes:
        id (int): Primary key, unique identifier for the patient
        user_id (int): Foreign key linking to User model
        contact_info (str): Patient's contact information
        age (int): Patient's age
        gender (str): Patient's gender
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    contact_info = db.Column(db.String(200))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))

    # Relationship: One Patient can have multiple Appointments
    appointments = db.relationship('Appointment', backref='patient')


class Appointment(db.Model):
    """
    Appointment Model - Represents appointments between doctors and patients
    
    Attributes:
        id (int): Primary key, unique identifier for the appointment
        doctor_id (int): Foreign key linking to Doctor model
        patient_id (int): Foreign key linking to Patient model
        date (date): Date of the appointment
        time (time): Time of the appointment
        status (str): Appointment status (e.g., 'Booked', 'Completed', 'Cancelled')
    """
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='Booked')

    # Relationship: One Appointment can have one Treatment record
    treatment = db.relationship('Treatment', backref='appointment', uselist=False)


class Treatment(db.Model):
    """
    Treatment Model - Stores medical treatment records for appointments
    
    Attributes:
        id (int): Primary key, unique identifier for the treatment record
        appointment_id (int): Foreign key linking to Appointment model
        diagnosis (str): Medical diagnosis
        prescription (str): Prescribed medications and treatment plan
        notes (str): Additional medical notes
    """
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)


class Department(db.Model):
    """
    Department Model - Represents hospital departments
    
    Attributes:
        id (int): Primary key, unique identifier for the department
        name (str): Department name (e.g., Cardiology, Emergency)
        description (str): Department description and details
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)      


# Ensure `db` is properly initialized and exported
__all__ = ['db', 'User', 'Doctor', 'Patient', 'Appointment', 'Treatment', 'Department']