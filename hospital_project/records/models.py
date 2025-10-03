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

    def __str__(self):
        return self.name

class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    # --- NEECHE DI GAYI DO LINES ADD KAREIN ---
    email = models.EmailField(unique=True, null=True)
    password_hash = models.CharField(max_length=100, null=True)
    
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
