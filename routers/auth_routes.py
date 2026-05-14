from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
import models, schemas, auth
from database import get_db

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

@router.post("/register", response_model=schemas.Patient)
def register_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    db_user = auth.get_user_by_phone(db, phone_number=patient.phone_number)
    if db_user:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    hashed_password = auth.get_password_hash(patient.password)
    db_patient = models.Patient(
        first_name=patient.first_name,
        last_name=patient.last_name,
        phone_number=patient.phone_number,
        email=patient.email,
        hashed_password=hashed_password
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

@router.post("/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # form_data.username as phone_number here
    user = auth.get_user_by_phone(db, phone_number=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"sub": user.phone_number}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.Patient)
def read_users_me(current_user: models.Patient = Depends(auth.get_current_user)):
    return current_user
