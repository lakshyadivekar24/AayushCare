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
    
    path('api/chat/', views.chat_api_view, name='chat_api'),
    
    path('diet-advisor/', views.diet_advisor_view, name='diet_advisor'),
    path('api/diet-advice/', views.diet_advice_api_view, name='diet_advice_api'),
    
    path('records/', views.medical_records_view, name='medical_records'),
    
    
    path('scanner/', views.scanner_view, name='scanner'),
    path('api/analyze-ingredients/', views.analyze_ingredients_api_view, name='analyze_ingredients_api'),
    
    path('book-appointment/', views.book_appointment_view, name='book_appointment'),
    
    path('doctor/appointments/', views.doctor_appointments_view, name='doctor_appointments'),
    path('doctor/appointments/update/<int:appointment_id>/', views.update_appointment_status_view, name='update_appointment_status'),

    path('doctor/patient/<int:patient_id>/add-record/', views.add_record_for_patient_view, name='add_record_for_patient'),

    path('doctor/search/', views.search_patient_view, name='search_patient'),
    
    path('doctor/conditions/', views.manage_conditions_view, name='manage_conditions'),
    
    path('doctor/profile/', views.doctor_profile_view, name='doctor_profile'),
    path('doctor/profile/edit/', views.edit_doctor_profile_view, name='edit_doctor_profile'),
    
    path('patient/onboarding/<int:step>/', views.patient_onboarding_view, name='patient_onboarding'),
    path('patient/profile/', views.patient_profile_view, name='patient_profile'),
    
    path('patient/profile/edit/', views.edit_patient_profile_view, name='edit_patient_profile'),

    # Home page URL
    path('', views.home_view, name='home'),
]