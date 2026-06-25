from django.db import models
from accounts.models import User
from doctors.models import AvailabilitySlot

class Appointment(models.Model):
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    slot = models.OneToOneField(
        AvailabilitySlot,
        on_delete=models.CASCADE,
        related_name='appointment'
    )
    booked_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.patient.username} → Dr.{self.slot.doctor.username} | {self.slot.date} {self.slot.start_time}"
