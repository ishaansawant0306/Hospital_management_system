# Database models for Hospital Management System
# Author: Ishaan Sawant
# This file contains all database table definitions using SQLAlchemy ORM

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Create database instance
db = SQLAlchemy()


# ==================== USER MODEL ====================
class User(db.Model):
    """
    Main user table - stores login credentials and role info
    Each user can be either Admin, Doctor, or Patient
    """
    __tablename__ = 'user'
    
    # Primary fields
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(200), nullable=False)  # Stores hashed password
    role = db.Column(db.String(20), nullable=False)  # Values: 'Admin', 'Doctor', 'Patient'
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationship links - a user has either doctor OR patient profile
    doctor = db.relationship('Doctor', backref='user', uselist=False, cascade='all, delete-orphan')
    patient = db.relationship('Patient', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def get_role(self):
        """Returns the role of this user"""
        return self.role
    
    def is_active(self):
        """Check if user account is active (not blacklisted)"""
        return not self.is_blacklisted
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


# ==================== DOCTOR MODEL ====================
class Doctor(db.Model):
    """
    Doctor profile table - extends User with doctor-specific data
    Linked to User table via user_id foreign key
    """
    __tablename__ = 'doctor'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    doctor_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    specialization = db.Column(db.String(100), nullable=False)
    availability = db.Column(db.String, nullable=True)  # JSON string of available slots
    address = db.Column(db.String(300), nullable=True)
    
    # One doctor can have many appointments
    appointments = db.relationship('Appointment', backref='doctor', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_full_name(self):
        """Get doctor's full name from linked user"""
        return self.user.username if self.user else 'Unknown'
    
    def __repr__(self):
        return f'<Doctor {self.doctor_id} - {self.specialization}>'


# ==================== PATIENT MODEL ====================
class Patient(db.Model):
    """
    Patient profile table - stores patient medical info
    Connected to User table through user_id
    """
    __tablename__ = 'patient'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    contact_info = db.Column(db.String(200))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    
    # One patient can book multiple appointments
    appointments = db.relationship('Appointment', backref='patient', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_patient_name(self):
        """Retrieve patient name from user table"""
        return self.user.username if self.user else 'Unknown Patient'
    
    def __repr__(self):
        return f'<Patient ID:{self.id} Age:{self.age}>'


# ==================== APPOINTMENT MODEL ====================
class Appointment(db.Model):
    """
    Appointment booking table
    Links doctors and patients with scheduled date/time
    """
    __tablename__ = 'appointment'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='Booked')  # Booked, Completed, Cancelled
    
    # Each appointment can have one treatment record
    treatment = db.relationship('Treatment', backref='appointment', uselist=False, cascade='all, delete-orphan')
    
    def is_completed(self):
        """Check if appointment is marked as completed"""
        return self.status == 'Completed'
    
    def is_cancelled(self):
        """Check if appointment was cancelled"""
        return self.status == 'Cancelled'
    
    def __repr__(self):
        return f'<Appointment {self.id}: Dr.{self.doctor_id} - Patient.{self.patient_id} on {self.date}>'


# ==================== TREATMENT MODEL ====================
class Treatment(db.Model):
    """
    Medical treatment records
    Stores diagnosis, prescription, and notes for each appointment
    """
    __tablename__ = 'treatment'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False, unique=True)
    diagnosis = db.Column(db.Text)  # Doctor's diagnosis
    prescription = db.Column(db.Text)  # Prescribed medicines
    notes = db.Column(db.Text)  # Additional medical notes (can be JSON)
    
    def has_prescription(self):
        """Check if prescription was provided"""
        return bool(self.prescription)
    
    def __repr__(self):
        return f'<Treatment for Appointment {self.appointment_id}>'


# ==================== DEPARTMENT MODEL ====================
class Department(db.Model):
    """
    Hospital departments table
    Stores department names and descriptions
    """
    __tablename__ = 'department'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Department: {self.name}>'


# Export all models
__all__ = ['db', 'User', 'Doctor', 'Patient', 'Appointment', 'Treatment', 'Department']