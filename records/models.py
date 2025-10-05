# records/models.py file me

from django.db import models
from django.utils import timezone

class Patient(models.Model):
    name = models.CharField(max_length=100)
    aadhar_number = models.CharField(max_length=12, unique=True)
    date_of_birth = models.DateField()
    # --- NEECHE DI GAYI DO LINES ADD KAREIN ---
    email = models.EmailField(unique=True, null=True)
    password_hash = models.CharField(max_length=100, null=True)
    profile_picture = models.ImageField(upload_to='patient_dps/', null=True, blank=True)
    
     # --- YEH NAYE ONBOARDING FIELDS HAIN ---
    # Step 1: Basic Info
    blood_group = models.CharField(max_length=5, null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True, help_text="Height in cm")
    weight = models.PositiveIntegerField(null=True, blank=True, help_text="Weight in kg")

    # Step 2: Lifestyle Info
    allergies = models.TextField(null=True, blank=True, help_text="List any known allergies")
    chronic_diseases = models.TextField(null=True, blank=True, help_text="List any chronic diseases like Diabetes, Hypertension")
    
    # Onboarding completion flag
    onboarding_complete = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    # --- NEECHE DI GAYI DO LINES ADD KAREIN ---
    email = models.EmailField(unique=True, null=True)
    password_hash = models.CharField(max_length=100, null=True)
    # --- YEH NAYE FIELDS HAIN ---
    gender = models.CharField(max_length=10, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    experience = models.PositiveIntegerField(null=True, blank=True, help_text="Experience in years")
    registration_no = models.CharField(max_length=50, null=True, blank=True)
    affiliation = models.CharField(max_length=200, null=True, blank=True, help_text="e.g., Apollo Hospital, Indore")
    
    # Practice Information
    clinic_address = models.TextField(null=True, blank=True)
    consultation_hours = models.CharField(max_length=100, null=True, blank=True, help_text="e.g., 10:00 AM - 06:00 PM")
    languages_spoken = models.CharField(max_length=200, null=True, blank=True, help_text="e.g., Hindi, English")
    consultation_modes = models.CharField(max_length=200, null=True, blank=True, help_text="e.g., In-person, Video")
    
    # Qualifications
    qualifications = models.TextField(null=True, blank=True, help_text="Add each qualification on a new line.")
    
    profile_picture = models.ImageField(upload_to='doctor_dps/', null=True, blank=True)

    
    def __str__(self):
        return self.name

class MedicalRecord(models.Model):
    # Isme koi change nahi hai
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    symptoms = models.TextField(null=True, blank=True)
    diagnosis = models.TextField(null=True, blank=True)
    prescription = models.TextField(null=True, blank=True)
    dose = models.CharField(max_length=50, null=True, blank=True)
    record_date = models.DateField(auto_now_add=True)

    # --- YEH NAYA FIELD ADD KAREIN ---
    report_file = models.FileField(upload_to='health_reports/', null=True, blank=True)

    def __str__(self):
        return f"Record for {self.patient.name} by {self.doctor.name}"

class PatientCondition(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    condition_name = models.CharField(max_length=255) # Jaise 'Pregnancy', 'Diabetes'
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True) # Shuruaat me khaali rahega

    def __str__(self):
        status = "Active" if self.end_date is None else f"Completed on {self.end_date}"
        return f"{self.condition_name} for {self.patient.name} ({status})"

# records/models.py

class Appointment(models.Model):
    MODE_CHOICES = [
        ('IN_CLINIC', 'In-Clinic Visit'),
        ('VIDEO_CALL', 'Video Call'),
        ('AUDIO_CALL', 'Audio Call'),
    ]
    
    STATUS_CHOICES = [
        ('Pending Confirmation', 'Pending Confirmation'),
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment_datetime = models.DateTimeField()
    reason = models.TextField()
    
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='Pending Confirmation'
    )
    
    mode = models.CharField(
        max_length=20,
        choices=MODE_CHOICES,
        default='IN_CLINIC'
    )

    def __str__(self):
        return f"{self.get_mode_display()} for {self.patient.name} with {self.doctor.name}"