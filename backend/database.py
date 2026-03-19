from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# SQLite database URL
DATABASE_URL = "sqlite:///./diabetes_predictions.db"

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class PredictionRecord(Base):
    """Model to store diabetes prediction records"""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, index=True)
    gender = Column(String)
    age = Column(Integer)
    hypertension = Column(Integer)
    heart_disease = Column(Integer)
    smoking_history = Column(String)
    bmi = Column(Float)
    hba1c_level = Column(Float)
    blood_glucose_level = Column(Float)
    prediction = Column(Integer)  # 0 for Not Diabetic, 1 for Diabetic
    probability = Column(Float)
    result = Column(String)  # "Diabetic" or "Not Diabetic"
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# Create all tables
Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
