from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('add-slot/', views.add_slot, name='add_slot'),
    path('delete-slot/<int:slot_id>/', views.delete_slot, name='delete_slot'),
]
