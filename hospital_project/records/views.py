# records/views.py

from django.shortcuts import render, redirect
from .models import Patient, Doctor, MedicalRecord, PatientCondition
import bcrypt
from django.http import JsonResponse
import json
from django.conf import settings
import google.generativeai as genai

# (Yahan aap apne register.py aur login.py ke functions ka logic use karenge)

def signup_view(request):
    if request.method == 'POST':
        # Form se data lein
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        # ... baaki fields
        
        # Password ko hash karein
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        # Naya patient banayein aur save karein
        Patient.objects.create(
            name=name,
            email=email,
            password_hash=hashed_password.decode('utf-8'),
            # ... baaki fields ke liye data daalein
            aadhar_number=request.POST.get('aadhar'),
            date_of_birth=request.POST.get('dob')
        )
        return redirect('login') # Register hone ke baad login page par bhej dein
    
    return render(request, 'records/signup.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type') # 'patient' ya 'doctor'

        user = None
        if user_type == 'patient':
            try:
                user = Patient.objects.get(email=email)
            except Patient.DoesNotExist:
                pass # User nahi mila
        elif user_type == 'doctor':
            try:
                user = Doctor.objects.get(email=email)
            except Doctor.DoesNotExist:
                pass # Doctor nahi mila
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            # Login successful, session me details save karein
            request.session['user_id'] = user.id
            request.session['user_type'] = user_type
            
            if user_type == 'patient':
                return redirect('patient_dashboard')
            elif user_type == 'doctor':
                return redirect('doctor_dashboard')
        else:
            # Login failed
            return render(request, 'records/login.html', {'error': 'Galat email ya password'})

    return render(request, 'records/login.html')

def logout_view(request):
    # Session clear karein
    request.session.flush()
    return redirect('login')

# Abhi ke liye dashboards ke simple versions
def patient_dashboard_view(request):
    if 'user_id' in request.session and request.session['user_type'] == 'patient':
        # Logged-in patient ko dhoondhein
        patient = Patient.objects.get(id=request.session['user_id'])
        
        # Us patient ke saare medical records dhoondhein
        medical_records = MedicalRecord.objects.filter(patient=patient)
        
        # <-- NAYA CHANGE: Us patient ki saari conditions dhoondhein
        patient_conditions = PatientCondition.objects.filter(patient=patient).order_by('-start_date')

        # Saara data template ko bhejein
        context = {
            'patient': patient,
            'records': medical_records,
            'conditions': patient_conditions, # <-- NAYA CHANGE
        }
        return render(request, 'records/patient_dashboard.html', context)
        
    return redirect('login')

def doctor_dashboard_view(request):
    # Pehle, check karein ki doctor logged in hai ya nahi
    if 'user_id' not in request.session or request.session.get('user_type') != 'doctor':
        return redirect('login')

    doctor = Doctor.objects.get(id=request.session['user_id'])

    # Agar form submit hua hai (POST request), to use handle karein
    if request.method == 'POST':
        # Yeh Naya Medical Record add karne ka logic hai
        patient_id = request.POST.get('patient')
        if patient_id:
            try:
                patient = Patient.objects.get(id=patient_id)
                MedicalRecord.objects.create(
                    doctor=doctor,
                    patient=patient,
                    symptoms=request.POST.get('symptoms'),
                    diagnosis=request.POST.get('diagnosis'),
                    prescription=request.POST.get('prescription'),
                    dose=request.POST.get('dose'),
                    report_file=request.FILES.get('report_file')
                )
            except Patient.DoesNotExist:
                # Handle case where patient ID is invalid
                pass
        # Kaam poora hone ke baad wapas dashboard par bhej dein
        return redirect('doctor_dashboard')

    # Agar normal page load hai (GET request), to saara data fetch karke dikhayein
    patients = Patient.objects.all()
    records_by_doctor = MedicalRecord.objects.filter(doctor=doctor)
    active_conditions = PatientCondition.objects.filter(end_date__isnull=True)
    
    context = {
        'doctor': doctor,
        'patients': patients,
        'records': records_by_doctor,
        'active_conditions': active_conditions,
    }
    return render(request, 'records/doctor_dashboard.html', context)


def home_view(request):
    if 'user_id' in request.session:
        if request.session['user_type'] == 'patient':
            return redirect('patient_dashboard')
        else:
            return redirect('doctor_dashboard')
    return redirect('login')

def doctor_signup_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        specialty = request.POST.get('specialty')
        password = request.POST.get('password')

        # Password ko hash karein
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        # Naya Doctor banayein aur save karein
        Doctor.objects.create(
            name=name,
            email=email,
            specialty=specialty,
            password_hash=hashed_password.decode('utf-8')
        )
        # Register hone ke baad login page par bhej dein
        return redirect('login')
    
    return render(request, 'records/doctor_signup.html')

# records/views.py me yeh dono functions hone chahiye

# Yeh function "Add Condition" waale form ko handle karta hai
def add_condition_view(request):
    if request.method == 'POST' and 'user_id' in request.session:
        patient_id = request.POST.get('patient')
        condition_name = request.POST.get('condition_name')
        start_date = request.POST.get('start_date')
        
        patient = Patient.objects.get(id=patient_id)
        
        PatientCondition.objects.create(
            patient=patient,
            condition_name=condition_name,
            start_date=start_date
        )
    return redirect('doctor_dashboard')

# Yeh function "Edit / Complete" button ko handle karta hai
def edit_condition_view(request, condition_id):
    condition = PatientCondition.objects.get(id=condition_id)

    if request.method == 'POST':
        end_date_str = request.POST.get('end_date')
        if end_date_str:
            condition.end_date = end_date_str
            condition.save()
        return redirect('doctor_dashboard')

    return render(request, 'records/edit_condition.html', {'condition': condition})

'''
def edit_condition_view(request, condition_id):
    # Condition ko uski ID se dhoondhein
    condition = PatientCondition.objects.get(id=condition_id)

    if request.method == 'POST':
        # Form se submit ki gayi end_date ko lein
        end_date_str = request.POST.get('end_date')
        if end_date_str:
            condition.end_date = end_date_str
            condition.save()
        # Kaam poora hone ke baad wapas dashboard par bhej dein
        return redirect('doctor_dashboard')

    # Agar POST request nahi hai, to form waala page dikhayein
    return render(request, 'records/edit_condition.html', {'condition': condition})
'''

def chat_api_view(request):
    # Step A: Check karein ki patient logged in hai
    if 'user_id' not in request.session or request.session.get('user_type') != 'patient':
        return JsonResponse({'error': 'Authentication required'}, status=401)

    # Step B: User ka message JSON se nikalein
    try:
        data = json.loads(request.body)
        user_message = data.get('message')
        if not user_message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)

    # Step C: Sirf uss logged-in patient ka data database se nikalein
    patient = Patient.objects.get(id=request.session['user_id'])
    records = MedicalRecord.objects.filter(patient=patient).select_related('doctor').order_by('-record_date')
    conditions = PatientCondition.objects.filter(patient=patient)

    # Step D: AI ke liye poora context (history) banayein
    history_text = f"Patient Name: {patient.name}, DOB: {patient.date_of_birth}\n"
    history_text += "Active Conditions:\n"
    active_conditions_list = list(conditions.filter(end_date__isnull=True))
    if active_conditions_list:
        for cond in active_conditions_list:
            history_text += f"- {cond.condition_name} (since {cond.start_date})\n"
    else:
        history_text += "- Koi active condition nahi hai.\n"
    
    history_text += "\nPast Medical Records:\n"
    if records:
        for rec in records:
            history_text += f"- Date: {rec.record_date}, Doctor: {rec.doctor.name}, Symptoms: {rec.symptoms}, Diagnosis: {rec.diagnosis}\n"
    else:
        history_text += "- Koi purana medical record nahi hai.\n"
        
    # Step E: Gemini API ko Configure aur Call Karein
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('models/gemini-pro-latest')

        prompt = f"""
                You are a helpful medical AI assistant for 'AayushCare'.
                Your knowledge is strictly limited to the patient data and the 'Safe Medicine List' provided below.

                --- SAFE MEDICINE LIST START ---
                - Headache (Sar Dard): Paracetamol (if no liver disease), Ibuprofen (if no stomach issues or kidney disease)
                - Common Cold (Sardi/Zukam): Cetirizine
                - Acidity (Gas): Antacid Gel
                - General Body Pain: Paracetamol
                --- SAFE MEDICINE LIST END ---

                --- PATIENT'S DATA START ---
                {history_text}
                --- PATIENT'S DATA END ---

                PATIENT'S QUESTION: "{user_message}"

                Your task:
                1.  Analyze the patient's question and their symptoms.
                2.  Check the patient's 'Active Conditions' from their data.
                3.  Look up the symptom in the 'Safe Medicine List'.
                4.  **CRITICAL:** Cross-check if the suggested medicine is safe considering the patient's 'Active Conditions'. For example, if a patient has a known allergy to a drug, DO NOT suggest it.
                5.  If a safe medicine is found in the list, you can suggest it.
                6.  **ALWAYS, without fail, end your response by advising the user to consult a real doctor before taking any medication.**

                ASSISTANT'S RESPONSE (in Hinglish):
                """

        response = model.generate_content(prompt)
        ai_response = response.text
    
    except Exception as e:
        # Agar AI API me koi error aaye
        ai_response = "Sorry, main abhi aapse connect nahi kar paa raha hoon. Kripya thodi der baad try karein."
        print(f"AI API Error: {e}")

    # Step F: Jawaab wapas front-end ko bhejein
    return JsonResponse({'reply': ai_response})

