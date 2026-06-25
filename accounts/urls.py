from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_choice_view, name='signup'),
    path('signup/doctor/', views.doctor_signup_view, name='doctor_signup'),
    path('signup/patient/', views.patient_signup_view, name='patient_signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]