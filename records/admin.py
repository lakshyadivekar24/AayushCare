# records/admin.py me

from django.contrib import admin
from .models import Patient, Doctor, MedicalRecord, PatientCondition # <-- PatientCondition ko import karein

# Register your models here.
admin.site.register(Patient)
admin.site.register(Doctor)
admin.site.register(MedicalRecord)
admin.site.register(PatientCondition) # <-- Is line ko add karein