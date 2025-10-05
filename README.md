<!-- Beautiful Animated Header -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:30D5C8,100:04619F&height=200&section=header&text=🏥%20Aayush%20Care🩺&fontSize=30&fontColor=fff&animation=fadeIn&fontAlignY=35" alt="Banner"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python" alt="Python Badge"/>
  <img src="https://img.shields.io/badge/Django-5.0-darkgreen?logo=django" alt="Django Badge"/>
  <img src="https://img.shields.io/badge/Database-SQLite3-lightgrey?logo=sqlite" alt="SQLite Badge"/>
  <img src="https://img.shields.io/github/last-commit/YourUsername/hospital_project" alt="Last Commit Badge"/>
  <img src="https://img.shields.io/github/license/YourUsername/hospital_project" alt="License Badge"/>
</p>

---

## 🌍 **About the Project**

**AayushCare** is a fully functional web application built with **Django** to simplify hospital operations — managing patients, doctors, appointments, and medical records all in one place.  
The project follows a clean, modular architecture and includes role-based access for **Admin**, **Doctor**, and **Patient** dashboards.

---

## 🚀 **Key Features**

- 👩‍⚕️ Doctor, Patient, and Admin Login  
- 🕓 Appointment Scheduling System  
- 🧾 Patient Record Management  
- 💊 Prescription & Diagnosis Tracking  
- 📁 File Upload for Reports  
- 📊 Interactive Dashboards  
- 🔐 Secure Authentication  
- 💻 Responsive UI (Bootstrap-based)

---

## 🧱 **Project Structure**

📦 hospital_project/ # Main project folder
│
├── 🧩 hospital_project/ # Django project configuration
│ ├── init.py
│ ├── settings.py # Project settings (Database, Middleware, etc.)
│ ├── urls.py # Root URL configuration
│ ├── wsgi.py # WSGI for deployment
│ └── asgi.py # ASGI for async server support
│
├── 📁 records/ # Main application (App)
│ ├── init.py
│ ├── admin.py # Django admin configuration
│ ├── apps.py # App config class
│ ├── models.py # Database models (Patients, Doctors, Appointments, etc.)
│ ├── urls.py # App-level URL routing
│ ├── views.py # All app logic and view functions
│ │
│ ├── 📂 templates/ # HTML templates
│ │ └── records/
│ │ ├── base.html # Common layout for all pages
│ │ ├── dashboard.html # Dashboard UI
│ │ ├── login.html # Login page
│ │ ├── appointments.html # Appointment page
│ │ └── patients.html # Patient records page
│ │
│ ├── 📂 static/ # (Optional) Static files (CSS, JS, images)
│ │ ├── css/
│ │ ├── js/
│ │ └── images/
│ │
│ └── 📂 migrations/ # Database migrations
│ └── init.py
│
├── 📜 manage.py # Django CLI manager
├── 📄 requirements.txt # Python dependencies
├── ⚙️ .gitignore # Files to ignore on GitHub
└── 🧾 README.md # Project documentation


---

## ⚙️ **Installation & Setup Guide**

### 🧩 1. Clone this Repository
```bash
git clone https://github.com/<your-username>/hospital_project.git
cd hospital_project
python -m venv venv
source venv/bin/activate      # (Mac/Linux)
venv\Scripts\activate         # (Windows)

pip install -r requirements.txt

python manage.py migrate

python manage.py createsuperuser

python manage.py runserver
