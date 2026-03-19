from fastapi import FastAPI, Depends
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session
import joblib
import numpy as np
from database import SessionLocal, PredictionRecord, get_db

app = FastAPI(title="Diabetes Prediction API")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Load model and encoders
# wrap in try block to provide clearer errors if dependencies are missing or incompatible
try:
    model = joblib.load("diabetes_model.pkl")
    gender_encoder = joblib.load("gender_encoder.pkl")
    smoking_encoder = joblib.load("smoking_encoder.pkl")
    scaler = joblib.load("scaler.pkl")  # Load scaler that was used during training
except FileNotFoundError as file_err:
    # Missing model/encoder/scaler files
    raise RuntimeError(
        f"Missing required model file: {file_err.filename}. "
        f"Please run 'python diabetes_predictor.py' to train and save the model."
    ) from file_err
except ModuleNotFoundError as load_err:
    # Common cause: numpy installation is broken or incompatible with saved pickle
    raise RuntimeError(
        "Failed to load serialized objects. "
        "This often occurs when numpy is not installed or the environment differs from the one used to save the model. "
        "Reinstall numpy (`pip install --upgrade numpy`) and ensure the versions match."
    ) from load_err
except ValueError as val_err:
    # catch numpy dtype size or other binary incompatibilities
    msg = str(val_err)
    if "numpy.dtype size changed" in msg or "binary incompatibility" in msg:
        raise RuntimeError(
            "Detected a binary incompatibility between NumPy and another library (e.g. pandas/xgboost). "
            "This usually means NumPy was upgraded without rebuilding dependent packages. "
            "Try reinstalling numpy, pandas, and xgboost: ``pip install --upgrade --force-reinstall numpy pandas xgboost``. "
            "If the issue persists, recreate your virtual environment and reinstall from requirements.txt."
        ) from val_err
    else:
        # re-raise if it's some other issue
        raise


# -------- Input Schema --------
class DiabetesInput(BaseModel):
    user_name: str
    gender: str
    age: int
    hypertension: int
    heart_disease: int
    smoking_history: str
    bmi: float
    hba1c_level: float
    blood_glucose_level: int
    
    @validator("gender")
    def normalize_gender(cls, v):
        v = v.strip().lower()
        if v == "male":
            return "Male"
        elif v == "female":
            return "Female"
        raise ValueError("Gender must be Male or Female")

    @validator("smoking_history")
    def normalize_smoking(cls, v):
        v = v.strip().lower()
        mapping = {
            "never": "never",
            "current": "current",
            "not current": "not current",
            "ever": "ever",
            "no info": "No Info"
        }
        if v in mapping:
            return mapping[v]
        raise ValueError("Invalid smoking history")
    
@app.get("/")
def home():
    return {"message": "Diabetes Prediction API is running"}

@app.get("/predictions")
def get_all_predictions(db: Session = Depends(get_db)):
    """Retrieve all stored predictions"""
    predictions = db.query(PredictionRecord).all()
    return {
        "total": len(predictions),
        "predictions": [
            {
                "id": p.id,
                "user_name": p.user_name,
                "age": p.age,
                "gender": p.gender,
                "prediction": p.prediction,
                "result": p.result,
                "probability": p.probability,
                "created_at": p.created_at
            }
            for p in predictions
        ]
    }

@app.get("/predictions/{user_name}")
def get_user_predictions(user_name: str, db: Session = Depends(get_db)):
    """Retrieve predictions for a specific user"""
    predictions = db.query(PredictionRecord).filter(
        PredictionRecord.user_name == user_name
    ).all()
    
    return {
        "user_name": user_name,
        "total": len(predictions),
        "predictions": [
            {
                "id": p.id,
                "age": p.age,
                "gender": p.gender,
                "prediction": p.prediction,
                "result": p.result,
                "probability": p.probability,
                "created_at": p.created_at
            }
            for p in predictions
        ]
    }

@app.get("/predictions/record/{record_id}")
def get_prediction_by_id(record_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific prediction record"""
    prediction = db.query(PredictionRecord).filter(
        PredictionRecord.id == record_id
    ).first()
    
    if not prediction:
        return {"error": "Prediction record not found"}
    
    return {
        "id": prediction.id,
        "user_name": prediction.user_name,
        "gender": prediction.gender,
        "age": prediction.age,
        "hypertension": prediction.hypertension,
        "heart_disease": prediction.heart_disease,
        "smoking_history": prediction.smoking_history,
        "bmi": prediction.bmi,
        "hba1c_level": prediction.hba1c_level,
        "blood_glucose_level": prediction.blood_glucose_level,
        "prediction": prediction.prediction,
        "result": prediction.result,
        "probability": prediction.probability,
        "created_at": prediction.created_at
    }

@app.post("/predict")
def predict_diabetes(data: DiabetesInput, db: Session = Depends(get_db)):

    gender_encoded = gender_encoder.transform([data.gender.capitalize()])[0]
    smoking_encoded = smoking_encoder.transform([data.smoking_history])[0]

    # Create feature array with same order as training
    features_raw = np.array([[
        gender_encoded,
        data.age,
        data.hypertension,
        data.heart_disease,
        smoking_encoded,
        data.bmi,
        data.hba1c_level,
        data.blood_glucose_level
    ]])
    
    # CRITICAL: Scale features using the scaler from training
    # The model was trained on SCALED data, so we must scale prediction input too
    features_scaled = scaler.transform(features_raw)

    prediction = model.predict(features_scaled)[0]
    probability = model.predict_proba(features_scaled)[0].max()
    result_text = "Diabetic" if prediction == 1 else "Not Diabetic"

    # Save to database
    db_record = PredictionRecord(
        user_name=data.user_name,
        gender=data.gender,
        age=data.age,
        hypertension=data.hypertension,
        heart_disease=data.heart_disease,
        smoking_history=data.smoking_history,
        bmi=data.bmi,
        hba1c_level=data.hba1c_level,
        blood_glucose_level=data.blood_glucose_level,
        prediction=int(prediction),
        probability=float(probability),
        result=result_text
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return {
        "id": db_record.id,
        "prediction": int(prediction),
        "probability": round(float(probability), 4),
        "result": result_text,
        "saved": True
    }
