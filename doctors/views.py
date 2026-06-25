from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import AvailabilitySlot
from django.utils import timezone
import datetime

def doctor_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_doctor():
            messages.error(request, 'Access denied. Doctors only!')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper

@doctor_required
def doctor_dashboard(request):
    slots = AvailabilitySlot.objects.filter(
        doctor=request.user
    ).order_by('date', 'start_time')
    
    today = timezone.now().date()
    upcoming_slots = slots.filter(date__gte=today)
    
    context = {
        'slots': upcoming_slots,
        'total_slots': slots.count(),
        'booked_slots': slots.filter(is_booked=True).count(),
        'available_slots': slots.filter(is_booked=False).count(),
    }
    return render(request, 'doctors/dashboard.html', context)

@doctor_required
def add_slot(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        
        try:
            AvailabilitySlot.objects.create(
                doctor=request.user,
                date=date,
                start_time=start_time,
                end_time=end_time
            )
            messages.success(request, 'Slot added successfully!')
        except Exception as e:
            messages.error(request, 'This slot already exists!')
            
    return redirect('doctor_dashboard')

@doctor_required
def delete_slot(request, slot_id):
    slot = get_object_or_404(
        AvailabilitySlot, 
        id=slot_id, 
        doctor=request.user
    )
    if not slot.is_booked:
        slot.delete()
        messages.success(request, 'Slot deleted!')
    else:
        messages.error(request, 'Cannot delete a booked slot!')
    return redirect('doctor_dashboard')
