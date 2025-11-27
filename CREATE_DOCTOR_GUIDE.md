# Create Doctor Modal - Complete Guide

## Overview
The Create Doctor Modal allows admins to create new doctor profiles with comprehensive information including credentials, identification, and contact details.

## Fields Included

### Required Fields (marked with *)
1. **Full Name*** - Doctor's complete name (e.g., "Dr. John Doe")
2. **Email Address*** - Doctor's email for login (must be unique)
3. **Password*** - Secure password for doctor login
4. **Doctor ID*** - Unique identification number (e.g., "DOC-12345")
5. **Specialization/Department*** - Medical specialty (e.g., "Cardiology", "Neurology")

### Optional Fields
6. **Availability** - Doctor's working hours (e.g., "Mon-Fri 9AM-5PM")
7. **Address** - Doctor's address (multi-line text area)

## How It Works

### Frontend (CreateDoctorModal.vue)
- **Location**: `frontend-clean/src/components/modals/CreateDoctorModal.vue`
- **Features**:
  - Modern, responsive design with Bootstrap 5
  - Two-column layout for better organization
  - Real-time validation
  - Success/Error feedback
  - Auto-closes after successful creation
  - Icons for visual clarity

### Backend (admin_routes.py)
- **Endpoint**: `POST /api/admin/doctors`
- **Validations**:
  - All required fields must be present
  - Email must be unique
  - Doctor ID must be unique
  - Password is securely hashed using werkzeug
  - Username is auto-generated from name

### Database (models.py)
- **Doctor Table Fields**:
  - `id` - Auto-increment primary key
  - `user_id` - Foreign key to User table
  - `doctor_id` - Unique doctor identification (VARCHAR 50)
  - `specialization` - Medical specialty (VARCHAR 100)
  - `availability` - Working hours (TEXT)
  - `address` - Doctor's address (VARCHAR 300)

## Usage Instructions

### For Admin Users:
1. Navigate to Admin Dashboard
2. Click the green **"+ create"** button in the "Registered Doctors" section
3. Fill in all required fields (marked with red asterisk *)
4. Optionally fill in Availability and Address
5. Click **"Create Doctor"** button
6. Wait for success message
7. Modal will auto-close and doctor list will refresh

### Important Notes:
- **Doctor ID must be unique** - System will show error if duplicate
- **Email must be unique** - Cannot reuse existing emails
- **Password is hashed** - Stored securely in database
- **Doctors cannot register themselves** - Only admin can create doctor accounts
- **Doctors can only login** - Using email and password provided by admin

## Data Flow

```
Admin Dashboard
    ↓ (clicks "+ create")
CreateDoctorModal Opens
    ↓ (fills form and submits)
POST /api/admin/doctors
    ↓ (validates data)
Creates User Record (role: Doctor)
    ↓
Creates Doctor Record (linked to User)
    ↓
Returns Success Response
    ↓
Modal Closes & Dashboard Refreshes
    ↓
New Doctor Appears in List
```

## Error Handling

The modal handles various error scenarios:
- Missing required fields
- Duplicate email
- Duplicate doctor ID
- Network errors
- Server errors

All errors are displayed in a user-friendly alert box within the modal.

## Styling Features

- **Green gradient header** matching TryggHelse brand
- **Bootstrap Icons** for visual clarity
- **Responsive design** works on mobile and desktop
- **Smooth animations** on hover and interactions
- **Professional color scheme** with green accents
- **Clear visual hierarchy** with proper spacing

## Database Migration

A migration script was created to add new fields to existing databases:
- **File**: `backend/migrate_doctor_schema.py`
- **Run once**: `python migrate_doctor_schema.py`
- **What it does**:
  - Adds `doctor_id` column
  - Adds `address` column
  - Assigns temporary IDs to existing doctors
  - Creates unique index on `doctor_id`

## Testing Checklist

- [ ] Modal opens when clicking "+ create" button
- [ ] All fields are visible and properly labeled
- [ ] Required field validation works
- [ ] Unique doctor_id validation works
- [ ] Unique email validation works
- [ ] Success message appears after creation
- [ ] Modal auto-closes after success
- [ ] Doctor list refreshes automatically
- [ ] New doctor appears in the list
- [ ] Doctor can login with created credentials

## Future Enhancements (Optional)

- Auto-generate doctor ID based on pattern
- Department dropdown instead of text input
- Profile picture upload
- Phone number field with validation
- Date of joining field
- Qualification/degree fields
- License number field
