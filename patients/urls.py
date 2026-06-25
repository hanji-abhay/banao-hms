from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor/<int:doctor_id>/slots/', views.view_doctor_slots, name='view_doctor_slots'),
    path('book/<int:slot_id>/', views.book_slot, name='book_slot'),
]
