# records/views.py
from django.http import JsonResponse
from django.conf import settings
import json
from django.shortcuts import render, redirect
from .models import Patient, Doctor, MedicalRecord, PatientCondition, Appointment
import bcrypt
from django.http import JsonResponse
import json
from django.conf import settings
import google.generativeai as genai
import traceback
import easyocr
from django.views.decorators.csrf import csrf_exempt



# (Yahan aap apne register.py aur login.py ke functions ka logic use karenge)

def signup_view(request):
    if request.method == 'POST':
        # Form se data lein
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        aadhar_number=request.POST.get('aadhar')
        date_of_birth=request.POST.get('dob')
        
        # Password ko hash karein
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        # Naya patient banayein aur save karein
        new_patient = Patient.objects.create(
            name=name,
            email=email,
            password_hash=hashed_password.decode('utf-8'),
            aadhar_number=aadhar_number,
            date_of_birth=date_of_birth
        )
        
        # Signup ke turant baad user ko login karayein
        request.session['user_id'] = new_patient.id
        request.session['user_type'] = 'patient'
        
        # SABSE ZAROORI LINE: User ko Onboarding ke Step 1 par bhejein
        return redirect('patient_onboarding', step=1)
    
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
                pass
        return redirect('doctor_dashboard')

    # --- YAHAN NAYA BADLAAV HAI ---
    # Agar normal page load hai (GET request), to saara data fetch karke dikhayein
    
    # Form ke dropdown ke liye saare patients
    all_patients = Patient.objects.all()
    
    # Doctor ke dwara banaye gaye medical records
    records_by_doctor = MedicalRecord.objects.filter(doctor=doctor)
    
    # Sabhi patients ki active conditions
    active_conditions = PatientCondition.objects.filter(end_date__isnull=True)

    # Doctor ke liye aaye saare appointments (Requested aur Accepted)
    doctor_appointments = Appointment.objects.filter(doctor=doctor).order_by('appointment_datetime')
    
    context = {
        'doctor': doctor,
        'patients': all_patients,
        'records': records_by_doctor,
        'active_conditions': active_conditions,
        'appointments': doctor_appointments, # <-- Naya data template ko bhejein
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

        You must differentiate between two types of questions:
        1.  **Factual History Questions:** (e.g., "Who was my doctor?")
        2.  **Medical Advice Questions:** (e.g., "I have a headache, what should I do?")

        Your task:
        -   If the user asks a Factual History Question, answer it directly from the data. **DO NOT** add a warning or the [ADVICE] tag.
        
        -   If the user asks a Medical Advice Question about a symptom in the 'Safe Medicine List':
            1.  Check the patient's 'Active Conditions'.
            2.  If the suggested medicine from the list does NOT conflict with any active condition, you SHOULD suggest the medicine by name.
            3.  Your response for this case **MUST** start with the special tag **[ADVICE]**.
            4.  Your response **MUST** also end with the phrase: "Lekin, koi bhi dawai lene se pehle, ek asli doctor se zaroor poochein."

        -   If the user asks for advice on something NOT in the safe list, or if you are unsure, provide a general safe response (like rest, drink water). This response **MUST** also start with the **[ADVICE]** tag and end with the doctor consultation warning.

        --- SAFE MEDICINE LIST START ---
        - Headache (Sar Dard): Paracetamol
        - Common Cold (Sardi/Zukam): Cetirizine
        - Acidity (Gas): Antacid Gel
        - General Body Pain: Paracetamol
        --- SAFE MEDICINE LIST END ---

        --- PATIENT'S DATA START ---
        {history_text}
        --- PATIENT'S DATA END ---

        PATIENT'S QUESTION: "{user_message}"

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

def diet_advisor_view(request):
    return render(request, 'records/diet_advisor.html')

def diet_advice_api_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            disease = data.get('disease')
            medicine = data.get('medicine')
            lang = data.get('language', 'en')

            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            # --- YAHAN NAYA CHANGE HAI ---
            # Model ko configure karein taaki woh JSON output de
            model = genai.GenerativeModel(
                'models/gemini-pro-latest',
                generation_config={"response_mime_type": "application/json"}
            )
            
            # System aur User Prompts ko jod kar ek hi prompt banayein
            full_prompt = f"""
            You are an expert dietician. Your response MUST be in the {lang} language.
            Generate a list of foods to 'avoid' and 'recommend' based on the user's query.
            Structure your response ONLY as a JSON object with "avoid" and "recommend" keys, which are arrays of strings.

            User Query:
            - Disease: {disease}
            - Optional Medicine: {medicine or 'None'}
            """
            
            response = model.generate_content(full_prompt)
            
            print("\n============= RAW RESPONSE FROM GEMINI =============")
            print(f"Response Text: '{response.text}'")
            print("==================================================")

            advice_json = json.loads(response.text)
            return JsonResponse(advice_json)

        except Exception as e:
            error_traceback = traceback.format_exc()
            print("--- CRASH TRACEBACK ---")
            print(error_traceback)
            print("-------------------------")
            return JsonResponse({
                'error': 'Backend server par crash ho gaya.',
                'detail': str(e),
                'traceback': error_traceback
            }, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def scanner_view(request):
    return render(request, 'records/scanner.html')

reader = easyocr.Reader(['en'])
@csrf_exempt
def analyze_ingredients_api_view(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method."}, status=400)
    
    # --- YAHAN NAYA BADLAAV HAI ---
    # Check karein ki user (patient) logged in hai ya nahi
    if 'user_id' not in request.session or request.session.get('user_type') != 'patient':
        return JsonResponse({"error": "Authentication required. Please log in as a patient."}, status=401)
    
    try:
        if 'file' not in request.FILES:
            return JsonResponse({"error": "No image file provided."}, status=400)
        
        image_file = request.FILES['file']
        
        # Logged-in patient ki ID session se lein
        logged_in_patient_id = request.session['user_id']
        patient = Patient.objects.get(id=logged_in_patient_id)
        
        # Patient ki active conditions database se nikalein
        active_conditions = PatientCondition.objects.filter(patient=patient, end_date__isnull=True)
        
        # AI ke liye asli health profile banayein
        health_profile = {
            "conditions": [cond.condition_name for cond in active_conditions],
            "allergies": [] # Aap allergies ke liye bhi alag se model bana kar yahan daal sakte hain
        }
        
        # Baaki ka logic waise hi rahega...
        image_bytes = image_file.read()
        raw_text = " ".join(reader.readtext(image_bytes, detail=0, paragraph=True))
        
        if not raw_text:
            return JsonResponse({"error": "Could not detect any text on the label."}, status=400)

        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('models/gemini-pro-latest')

        prompt = f"""
        You are an expert AI Nutritionist for AyushCare.
        - User Health Profile: {json.dumps(health_profile)}
        - Raw OCR Text from Product Package: "{raw_text}"
        TASK:
        1. Locate the ingredients list in the Raw OCR Text.
        2. Compare each ingredient against the user's health profile.
        3. Provide a final verdict: "Safe", "Eat in Moderation", or "Not Recommended".
        4. Write a concise reason.
        5. List the specific ingredients you identified as risky.
        6. Suggest 1-2 safer alternative product types if the product is not "Safe".
        7. You MUST output your response ONLY as a single, valid JSON object with keys: "status", "reason", "risky_ingredients", "suggestions".
        """
        
        response = model.generate_content(prompt)
        cleaned_response_text = response.text.strip().replace('```json', '').replace('```', '')
        analysis_result = json.loads(cleaned_response_text)

        return JsonResponse({
            "health_analysis": analysis_result,
            "patient_name": patient.name  # <-- YEH NAYA ADD HUA HAI
        })

    except Exception as e:
        # ... (error handling waise hi rahega) ...
        print(f"Error in analyze_ingredients_api_view: {e}")
        return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)
    
def book_appointment_view(request):
    if 'user_id' not in request.session or request.session.get('user_type') != 'patient':
        return redirect('login')

    patient = Patient.objects.get(id=request.session['user_id'])

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        appointment_date = request.POST.get('date')
        appointment_time = request.POST.get('time')
        # Combine date and time into a single string that Django understands
        appointment_datetime_str = f"{appointment_date}T{appointment_time}"
        
        reason = request.POST.get('reason')
        mode = request.POST.get('mode')
        
        doctor = Doctor.objects.get(id=doctor_id)

        # --- THIS IS THE FIX ---
        Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            appointment_datetime=appointment_datetime_str, # Add this line
            reason=reason,
            mode=mode,
            status='Scheduled' 
        )
        return redirect('book_appointment')

    doctors = Doctor.objects.all()
    appointments = Appointment.objects.filter(patient=patient).order_by('-appointment_datetime')
    
    context = {
        'doctors': doctors,
        'appointments': appointments
    }
    return render(request, 'records/book_appointment.html', context)

def medical_records_view(request):
    # Check karein ki patient logged in hai ya nahi
    if 'user_id' not in request.session or request.session.get('user_type') != 'patient':
        return redirect('login')

    # Logged-in patient ki details nikalein
    patient = Patient.objects.get(id=request.session['user_id'])
    
    # Uss patient ke saare medical records, naye se purane order me, nikalein
    medical_records = MedicalRecord.objects.filter(patient=patient).order_by('-record_date')
    
    # Data ko template ko bhejein
    context = {
        'patient': patient,
        'records': medical_records,
    }
    return render(request, 'records/records.html', context)

def doctor_appointments_view(request):
    # Check karein ki doctor logged in hai
    if 'user_id' not in request.session or request.session.get('user_type') != 'doctor':
        return redirect('login')

    doctor = Doctor.objects.get(id=request.session['user_id'])
    
    # Doctor ke saare appointments, naye se purane order me, fetch karein
    all_appointments = Appointment.objects.filter(doctor=doctor).order_by('-appointment_datetime')
    
    context = {
        'doctor': doctor,
        'appointments': all_appointments
    }
    
    # Naye template ko render karein
    return render(request, 'records/doctor_appointments.html', context)

def update_appointment_status_view(request, appointment_id):
    # Sirf POST request ko allow karein
    if request.method == 'POST':
        # Check karein ki doctor logged in hai
        if 'user_id' not in request.session or request.session.get('user_type') != 'doctor':
            return redirect('login')

        try:
            # Appointment ko uski ID se dhoondhein
            appointment = Appointment.objects.get(id=appointment_id)
            # Doctor sirf apne hi appointment ko change kar sakta hai
            if appointment.doctor.id == request.session['user_id']:
                new_status = request.POST.get('status')
                # Check karein ki bheja gaya status valid hai
                valid_statuses = [choice[0] for choice in Appointment.STATUS_CHOICES]
                if new_status in valid_statuses:
                    appointment.status = new_status
                    appointment.save()
        except Appointment.DoesNotExist:
            pass # Agar appointment nahi mila to kuch na karein

    # Kaam poora hone ke baad wapas appointments page par bhej dein
    return redirect('doctor_appointments')

def search_patient_view(request):
    # Check karein ki doctor logged in hai ya nahi
    if 'user_id' not in request.session or request.session.get('user_type') != 'doctor':
        return redirect('login')

    # Default context
    context = {}
    doctor = Doctor.objects.get(id=request.session['user_id'])

    # Agar doctor ne form submit kiya hai (POST request)
    if request.method == 'POST':
        aadhar_query = request.POST.get('aadhar_number', '').strip()
        
        if aadhar_query:
            try:
                # Aadhar number se patient ko dhoondhein
                patient = Patient.objects.get(aadhar_number=aadhar_query)
                records = MedicalRecord.objects.filter(patient=patient).order_by('-record_date')
                
                context = {
                    'patient_found': True,
                    'patient': patient,
                    'records': records,
                    'search_query': aadhar_query
                }
            except Patient.DoesNotExist:
                context['error'] = f"'{aadhar_query}' Aadhar number waala koi patient nahi mila."
                context['search_query'] = aadhar_query
    
    # Agar normal page load hai (GET request) ya search ke baad,
    # doctor ki apni history bhi bhejein
    records_by_doctor = MedicalRecord.objects.filter(doctor=doctor).order_by('-record_date')
    context['records_by_doctor'] = records_by_doctor

    return render(request, 'records/search_patient.html', context)

def add_record_for_patient_view(request, patient_id):
    # Check karein ki doctor logged in hai
    if 'user_id' not in request.session or request.session.get('user_type') != 'doctor':
        return redirect('login')

    doctor = Doctor.objects.get(id=request.session['user_id'])
    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        # Agar galat ID se patient dhoondha jaaye to search page par bhej dein
        return redirect('search_patient')

    # Agar form submit hua hai
    if request.method == 'POST':
        MedicalRecord.objects.create(
            doctor=doctor,
            patient=patient,
            symptoms=request.POST.get('symptoms'),
            diagnosis=request.POST.get('diagnosis'),
            prescription=request.POST.get('prescription'),
            dose=request.POST.get('dose'),
            report_file=request.FILES.get('report_file')
        )
        # Record save hone ke baad, usi patient ke search result page par wapas bhej dein
        # Iske liye hum ek POST request bhejenge taaki view patient ko fir se search kar le
        return redirect('search_patient') # Simplest redirect

    # Agar normal page load hai (GET request), to form dikhayein
    context = {
        'patient': patient
    }
    return render(request, 'records/add_record_form.html', context)

def manage_conditions_view(request):
    # Check karein ki doctor logged in hai
    if 'user_id' not in request.session or request.session.get('user_type') != 'doctor':
        return redirect('login')

    # Agar form submit hua hai (POST request)
    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        condition_name = request.POST.get('condition_name')
        start_date = request.POST.get('start_date')
        
        patient = Patient.objects.get(id=patient_id)
        
        PatientCondition.objects.create(
            patient=patient,
            condition_name=condition_name,
            start_date=start_date
        )
        # Form submit hone ke baad usi page par wapas redirect kar dein
        return redirect('manage_conditions')

    # Agar normal page load hai (GET request)
    patients = Patient.objects.all()
    active_conditions = PatientCondition.objects.filter(end_date__isnull=True).order_by('-start_date')
    
    context = {
        'patients': patients,
        'active_conditions': active_conditions
    }
    return render(request, 'records/manage_conditions.html', context)

def doctor_profile_view(request):
    # Check karein ki doctor logged in hai
    if 'user_id' not in request.session or request.session.get('user_type') != 'doctor':
        return redirect('login')

    # Logged-in doctor ki details nikalein
    doctor = Doctor.objects.get(id=request.session['user_id'])
    
    context = {
        'doctor': doctor,
    }
    return render(request, 'records/doctor_profile.html', context)

def edit_doctor_profile_view(request):
    if 'user_id' not in request.session or request.session.get('user_type') != 'doctor':
        return redirect('login')

    doctor = Doctor.objects.get(id=request.session['user_id'])

    if request.method == 'POST':
        # Form se saara data update karein
        doctor.name = request.POST.get('name')
        doctor.gender = request.POST.get('gender')
        doctor.date_of_birth = request.POST.get('date_of_birth')
        doctor.phone = request.POST.get('phone')
        doctor.experience = request.POST.get('experience')
        doctor.registration_no = request.POST.get('registration_no')
        doctor.affiliation = request.POST.get('affiliation')
        doctor.clinic_address = request.POST.get('clinic_address')
        doctor.consultation_hours = request.POST.get('consultation_hours')
        doctor.languages_spoken = request.POST.get('languages_spoken')
        doctor.consultation_modes = request.POST.get('consultation_modes')
        doctor.qualifications = request.POST.get('qualifications')
        
        # Agar nayi profile picture upload hui hai to use save karein
        if 'profile_picture' in request.FILES:
            doctor.profile_picture = request.FILES['profile_picture']
            
        doctor.save()
        return redirect('doctor_profile') # Save karne ke baad profile page par bhej dein

    context = {'doctor': doctor}
    return render(request, 'records/edit_doctor_profile.html', context)

# records/views.py

def patient_onboarding_view(request, step):
    if 'user_id' not in request.session or request.session.get('user_type') != 'patient':
        return redirect('login')

    patient = Patient.objects.get(id=request.session['user_id'])
    
    # Initialize session data if it doesn't exist
    if 'onboarding_data' not in request.session:
        request.session['onboarding_data'] = {}

    if request.method == 'POST':
        if step == 1:
            # Step 1 ka data session me store karein
            data = request.session['onboarding_data']
            data['blood_group'] = request.POST.get('blood_group')
            data['height'] = request.POST.get('height')
            data['weight'] = request.POST.get('weight')
            request.session['onboarding_data'] = data
            return redirect('patient_onboarding', step=2) # Agle step par bhejein
        
        elif step == 2:
            # Step 2 ka data session me store karein
            data = request.session['onboarding_data']
            data['allergies'] = request.POST.get('allergies')
            data['chronic_diseases'] = request.POST.get('chronic_diseases')
            
            # Ab saara data session se nikal kar database me save karein
            patient.blood_group = data.get('blood_group')
            patient.height = data.get('height')
            patient.weight = data.get('weight')
            patient.allergies = data.get('allergies')
            patient.chronic_diseases = data.get('chronic_diseases')
            patient.onboarding_complete = True # Mark as complete
            patient.save()
            
            # Session data ko clear kar dein
            del request.session['onboarding_data']
            
            return redirect('patient_profile') # Profile page par bhejein

    # Current step ka template dikhayein
    # Hum hamesha ek hi template file render karenge
    return render(request, 'records/patient_onboarding.html', {'step': step})

def patient_profile_view(request):
    if 'user_id' not in request.session or request.session.get('user_type') != 'patient':
        return redirect('login')
    
    patient = Patient.objects.get(id=request.session['user_id'])
    context = {'patient': patient}
    return render(request, 'records/patient_profile.html', context)

# records/views.py me add karein

def edit_patient_profile_view(request):
    if 'user_id' not in request.session or request.session.get('user_type') != 'patient':
        return redirect('login')

    patient = Patient.objects.get(id=request.session['user_id'])

    if request.method == 'POST':
        # Form se data update karein
        patient.name = request.POST.get('name')
        patient.date_of_birth = request.POST.get('date_of_birth')
        patient.blood_group = request.POST.get('blood_group')
        patient.height = request.POST.get('height')
        patient.weight = request.POST.get('weight')
        patient.allergies = request.POST.get('allergies')
        patient.chronic_diseases = request.POST.get('chronic_diseases')
        
        # Agar nayi profile picture upload hui hai to use save karein
        if 'profile_picture' in request.FILES:
            patient.profile_picture = request.FILES['profile_picture']
            
        patient.save()
        return redirect('patient_profile') # Save karne ke baad profile page par bhej dein

    context = {'patient': patient}
    return render(request, 'records/edit_patient_profile.html', context)