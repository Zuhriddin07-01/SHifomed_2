from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class PatientBase(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    email: Optional[EmailStr] = None

class PatientCreate(PatientBase):
    password: str

class Patient(PatientBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    phone_number: Optional[str] = None

class DoctorBase(BaseModel):
    first_name: str
    last_name: str
    specialty: str
    experience_years: int
    image_url: Optional[str] = None

class Doctor(DoctorBase):
    id: int

    class Config:
        from_attributes = True

class AppointmentBase(BaseModel):
    doctor_id: int
    appointment_date: datetime

class AppointmentCreate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    id: int
    patient_id: int
    status: str
    created_at: datetime
    doctor: Doctor

    class Config:
        from_attributes = True
