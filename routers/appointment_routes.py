from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas, auth
from database import get_db

router = APIRouter(
    prefix="/api/appointments",
    tags=["Appointments"]
)

@router.post("/", response_model=schemas.Appointment)
def create_appointment(appointment: schemas.AppointmentCreate, db: Session = Depends(get_db), current_user: models.Patient = Depends(auth.get_current_user)):
    db_appointment = models.Appointment(
        patient_id=current_user.id,
        doctor_id=appointment.doctor_id,
        appointment_date=appointment.appointment_date,
        status="pending"
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@router.get("/me", response_model=List[schemas.Appointment])
def read_user_appointments(db: Session = Depends(get_db), current_user: models.Patient = Depends(auth.get_current_user)):
    appointments = db.query(models.Appointment).filter(models.Appointment.patient_id == current_user.id).order_by(models.Appointment.appointment_date.desc()).all()
    return appointments
