from django.urls import path
from . import views

urlpatterns = [
    # URLs for signup, login, and logout
    path('signup/', views.signup_view, name='signup'),
    path('signup/doctor/', views.doctor_signup_view, name='doctor_signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # URLs for dashboards
    path('patient/dashboard/', views.patient_dashboard_view, name='patient_dashboard'),
    path('doctor/dashboard/', views.doctor_dashboard_view, name='doctor_dashboard'),

    # YEH LINE MISSING THI, ISE ADD KAREIN
    path('condition/add/', views.add_condition_view, name='add_condition'),

    # This URL allows editing a condition to add an end date
    path('condition/edit/<int:condition_id>/', views.edit_condition_view, name='edit_condition'),
    
    # Home page URL
    path('', views.home_view, name='home'),
]