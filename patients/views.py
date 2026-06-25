from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from doctors.models import AvailabilitySlot
from appointments.models import Appointment
from accounts.models import User
from django.utils import timezone
import requests as http_requests
from appointments.calendar_service import create_calendar_event

def send_email_notification(trigger, email, name, extra_data={}):
    try:
        payload = {
            'trigger': trigger,
            'email': email,
            'name': name,
            **extra_data
        }
        http_requests.post(
            'http://localhost:4000/dev/send-email',
            json=payload,
            timeout=5
        )
    except Exception as e:
        print(f'Email service error: {e}')

def patient_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_patient():
            messages.error(request, 'Access denied. Patients only!')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper

@patient_required
def patient_dashboard(request):
    today = timezone.now().date()
    
    # all doctors
    doctors = User.objects.filter(role='doctor')
    
    # patient's own appointments
    my_appointments = Appointment.objects.filter(
        patient=request.user
    ).select_related('slot', 'slot__doctor').order_by('slot__date')
    
    context = {
        'doctors': doctors,
        'my_appointments': my_appointments,
    }
    return render(request, 'patients/dashboard.html', context)

@patient_required
def view_doctor_slots(request, doctor_id):
    doctor = get_object_or_404(User, id=doctor_id, role='doctor')
    today = timezone.now().date()
    
    # only future unbooked slots
    slots = AvailabilitySlot.objects.filter(
        doctor=doctor,
        date__gte=today,
        is_booked=False
    ).order_by('date', 'start_time')
    
    context = {
        'doctor': doctor,
        'slots': slots,
    }
    return render(request, 'patients/doctor_slots.html', context)

@patient_required
def book_slot(request, slot_id):
    if request.method == 'POST':
        # transaction.atomic handles race condition!
        try:
            with transaction.atomic():
                # select_for_update LOCKS the row
                # so two patients cant book simultaneously
                slot = AvailabilitySlot.objects.select_for_update().get(
                    id=slot_id,
                    is_booked=False
                )
                # create appointment
                Appointment.objects.create(
                    patient=request.user,
                    slot=slot
                )
                # mark slot as booked
                slot.is_booked = True
                slot.save()

                send_email_notification(
                    'BOOKING_CONFIRMATION',
                    request.user.email,
                    request.user.username,
                    {
                        'doctor': slot.doctor.username,
                        'date': str(slot.date),
                        'time': f'{slot.start_time} - {slot.end_time}'
                    }
                  )

                # Google Calendar events
                date_str = str(slot.date)
                start_str = str(slot.start_time)[:5]
                end_str = str(slot.end_time)[:5]

                # patient calendar event
                create_calendar_event(
                    f'token_patient_{request.user.id}.json',
                    f'Appointment with Dr. {slot.doctor.username}',
                    date_str,
                    start_str,
                    end_str,
                    f'Your appointment at HMS'
                )

                # doctor calendar event
                create_calendar_event(
                    f'token_doctor_{slot.doctor.id}.json',
                    f'Appointment with {request.user.username}',
                    date_str,
                    start_str,
                    end_str,
                    f'Patient appointment at HMS'
                )
                
                messages.success(request, f'Appointment booked successfully with Dr. {slot.doctor.username}!')
                return redirect('patient_dashboard')
                
        except AvailabilitySlot.DoesNotExist:
            messages.error(request, 'Sorry! This slot was just booked by someone else.')
            return redirect('patient_dashboard')
            
    return redirect('patient_dashboard')


