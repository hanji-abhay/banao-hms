
import requests as http_requests
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import SignupForm, LoginForm
from .models import User

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

def signup_choice_view(request):
    return render(request, 'accounts/signup_choice.html')

def doctor_signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'doctor'
            user.save()
            login(request, user)
            send_email_notification(
                'SIGNUP_WELCOME',
                user.email,
                user.username
            )
            messages.success(request, 'Doctor account created successfully!')
            return redirect('doctor_dashboard')
    else:
        form = SignupForm()
    return render(request, 'accounts/doctor_signup.html', {'form': form})

def patient_signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'patient'
            user.save()
            login(request, user)
            send_email_notification(
                'SIGNUP_WELCOME',
                user.email,
                user.username
            )
            messages.success(request, 'Patient account created successfully!')
            return redirect('patient_dashboard')
    else:
        form = SignupForm()
    return render(request, 'accounts/patient_signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_doctor():
                    return redirect('doctor_dashboard')
                else:
                    return redirect('patient_dashboard')
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')
