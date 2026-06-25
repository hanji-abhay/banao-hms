import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Email config
SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = 'abhaymathur629@gmail.com'
SMTP_PASSWORD = 'rucdfvioinfexjrg'

def send_email(event, context):
    try:
        # parse request body
        body = json.loads(event.get('body', '{}'))
        trigger = body.get('trigger')
        recipient = body.get('email')
        name = body.get('name', 'User')
        
        # build email based on trigger type
        if trigger == 'SIGNUP_WELCOME':
            subject = 'Welcome to HMS! 🏥'
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #667eea;">Welcome to HMS, {name}! 🏥</h2>
                <p>Your account has been created successfully.</p>
                <p>You can now log in and start using our hospital management system.</p>
                <br>
                <p>Best Regards,<br>HMS Team</p>
            </div>
            """
            
        elif trigger == 'BOOKING_CONFIRMATION':
            doctor = body.get('doctor', 'Doctor')
            date = body.get('date', '')
            time = body.get('time', '')
            subject = 'Appointment Confirmed! ✅'
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #48bb78;">Appointment Confirmed! ✅</h2>
                <p>Dear {name},</p>
                <p>Your appointment has been booked successfully!</p>
                <div style="background: #f7fafc; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                    <p><strong>Doctor:</strong> Dr. {doctor}</p>
                    <p><strong>Date:</strong> {date}</p>
                    <p><strong>Time:</strong> {time}</p>
                </div>
                <p>Please arrive 10 minutes early.</p>
                <br>
                <p>Best Regards,<br>HMS Team</p>
            </div>
            """
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid trigger type'})
            }

        # send email via SMTP
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SMTP_USER
        msg['To'] = recipient

        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, recipient, msg.as_string())

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': f'Email sent successfully!',
                'trigger': trigger,
                'recipient': recipient
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }