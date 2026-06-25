# HMS - Hospital Management System

A mini Hospital Management System built with Django, MySQL, Serverless Framework, and Google Calendar API.

## Setup and Run

### Prerequisites
- Python 3.11+
- MySQL
- Node.js
- Git

### 1. Clone the repository
```bash
git clone https://github.com/hanji-abhay/banao-hms.git
cd banao-hms
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup environment variables
Create a `.env` file in root folder:

SMTP_USER=yourgmail@gmail.com
SMTP_PASSWORD=your_app_password

### 5. Setup MySQL Database
Open MySQL and run:
```sql
CREATE DATABASE banao_hms;
```

Update `hms/settings.py` with your MySQL credentials.

### 6. Add Google Calendar credentials
- Go to Google Cloud Console
- Enable Google Calendar API
- Create OAuth2 credentials (Desktop app)
- Download as `credentials.json` and place in root folder

### 7. Run migrations
```bash
python manage.py migrate
```

### 8. Start Django server
```bash
python manage.py runserver
```

### 9. Start Serverless email service
```bash
cd email-service
npm install
serverless offline start
```

### 10. Access the app
Open browser → `http://127.0.0.1:8000`

---

## System Architecture

### Overview
The system consists of two separate services running locally:

1. **Django Application** (port 8000) — main web application
2. **Serverless Email Service** (port 4000) — handles all email notifications

### Data Models
- **User** — extends AbstractUser with a `role` field (doctor/patient)
- **AvailabilitySlot** — doctor's available time slots with `is_booked` flag
- **Appointment** — links a patient to a slot via OneToOneField

### Role Based Access
- Custom decorators `doctor_required` and `patient_required` check user role on every protected view
- Patients cannot access doctor views and vice versa
- Enforced at view level, not just template level

### Google Calendar Integration
- Uses OAuth2 with Desktop app credentials
- Separate token files per user (`token_patient_X.json`, `token_doctor_X.json`)
- On booking confirmation, creates calendar events for both doctor and patient
- Tokens are stored locally and refreshed automatically

### Django → Serverless Connection
- Django calls the serverless function via HTTP POST to `http://localhost:4000/dev/send-email`
- Serverless offline simulates AWS Lambda locally
- Email function supports two triggers: `SIGNUP_WELCOME` and `BOOKING_CONFIRMATION`

---

## The Design Decision

### Problem: Handling Race Conditions in Slot Booking

When two patients try to book the same slot simultaneously, without protection both could succeed — creating a double booking.

### Option 1: Application-level check
Check if slot is booked before creating appointment:
```python
if not slot.is_booked:
    slot.is_booked = True
    slot.save()
```
**Problem:** Two requests can pass the check simultaneously before either saves — classic race condition.

### Option 2: Database-level locking with select_for_update()
```python
with transaction.atomic():
    slot = AvailabilitySlot.objects.select_for_update().get(
        id=slot_id,
        is_booked=False
    )
```
**Why I chose this:** `select_for_update()` locks the database row at the database level — not application level. This means even if two requests arrive simultaneously, the database itself ensures only one transaction can hold the lock at a time. The second request waits, then fails gracefully with a DoesNotExist exception when the slot is already booked. This is not just safer — it is architecturally correct. Race conditions should be handled where data lives, not in application code.

---

## Limitations

### What would break in production:

1. **Token storage** — OAuth tokens stored as local JSON files. In production these should be stored in a database per user, encrypted.

2. **Serverless offline** — We use serverless-offline for local testing. Real AWS Lambda deployment would require AWS credentials and proper IAM roles.

3. **Single Google account assumption** — We assume one Google account per user. In production users would need to explicitly connect their Google account.

4. **No slot cancellation** — Patients cannot cancel bookings. This would be essential in production.

5. **Email reliability** — Gmail SMTP has daily sending limits. Production should use dedicated email services like SendGrid or AWS SES.

### What I would fix first:
Token storage in database — because it's a security risk to store OAuth tokens as plain JSON files on disk.