from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import models
from database import engine, SessionLocal
from routers import auth_routes, doctor_routes, appointment_routes
from sqladmin import Admin, ModelView

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SHIFOMED API",
    description="SHIFOMED tizimi uchun backend API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(doctor_routes.router)
app.include_router(appointment_routes.router)

app.mount("/static", StaticFiles(directory="static"), name="static")

# SQLAdmin setup
admin = Admin(app, engine)

class PatientAdmin(ModelView, model=models.Patient):
    column_list = [models.Patient.id, models.Patient.first_name, models.Patient.last_name, models.Patient.phone_number]

class DoctorAdmin(ModelView, model=models.Doctor):
    column_list = [models.Doctor.id, models.Doctor.first_name, models.Doctor.last_name, models.Doctor.specialty]

class AppointmentAdmin(ModelView, model=models.Appointment):
    column_list = [models.Appointment.id, models.Appointment.patient_id, models.Appointment.doctor_id, models.Appointment.appointment_date, models.Appointment.status]

admin.add_view(PatientAdmin)
admin.add_view(DoctorAdmin)
admin.add_view(AppointmentAdmin)

# Add dummy doctors
def create_dummy_doctors():
    db = SessionLocal()
    try:
        if db.query(models.Doctor).count() == 0:
            doctors = [
                models.Doctor(first_name="Alisher", last_name="Toxirov", specialty="Kardiolog", experience_years=10, image_url="👨‍⚕️"),
                models.Doctor(first_name="Zarina", last_name="Nazarova", specialty="Stomatolog", experience_years=5, image_url="👩‍⚕️"),
                models.Doctor(first_name="Dilmurod", last_name="Hasanov", specialty="Nevropatolog", experience_years=8, image_url="👨‍⚕️"),
            ]
            db.add_all(doctors)
            db.commit()
    finally:
        db.close()

create_dummy_doctors()

@app.get("/")
def read_root():
    return FileResponse("static/index.html")
