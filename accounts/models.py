from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    DOCTOR = 'doctor'
    PATIENT = 'patient'
    
    ROLE_CHOICES = [
        (DOCTOR, 'Doctor'),
        (PATIENT, 'Patient'),
    ]
    
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        null=False, 
        blank=False
    )
    phone = models.CharField(max_length=15, blank=True)
    
    def is_doctor(self):
        return self.role == self.DOCTOR
    
    def is_patient(self):
        return self.role == self.PATIENT
    
    def __str__(self):
        return f"{self.username} ({self.role})"