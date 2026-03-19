from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, validator
import joblib
import numpy as np
import os
from mangum import Mangum  # ✅ ADD THIS

# ✅ COMMENT OUT database for now (Vercel doesn't support SQLite)
# from database import SessionLocal, PredictionRecord, get_db

app = FastAPI(title="Diabetes Prediction API")

from fastapi.middleware.cors import CORSMiddleware

# ✅ FIX 1: Update CORS for Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://diabetes-frontend.vercel.app",  # Add your frontend URL
        "*"  # Temporary for testing
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ FIX 2: Use absolute paths for model files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load model and encoders with absolute paths
try:
    model_path = os.path.join(BASE_DIR, "diabetes_model.pkl")
    gender_encoder_path = os.path.join(BASE_DIR, "gender_encoder.pkl")
    smoking_encoder_path = os.path.join(BASE_DIR, "smoking_encoder.pkl")
    scaler_path = os.path.join(BASE_DIR, "scaler.pkl")
    
    print(f"Loading model from: {model_path}")  # Debug log
    
    model = joblib.load(model_path)
    gender_encoder = joblib.load(gender_encoder_path)
    smoking_encoder = joblib.load(smoking_encoder_path)
    scaler = joblib.load(scaler_path)
    
    print("✅ All models loaded successfully!")
    
except FileNotFoundError as file_err:
    print(f"❌ File not found: {file_err}")
    raise RuntimeError(f"Missing model file: {file_err.filename}")
except Exception as e:
    print(f"❌ Error loading models: {e}")
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
    return {
        "message": "Diabetes Prediction API is running",
        "status": "healthy",
        "models_loaded": True
    }

# ✅ FIX 3: Comment out database endpoints for now
"""
@app.get("/predictions")
def get_all_predictions():
    return {"message": "Database endpoints disabled on Vercel"}
"""

@app.post("/predict")
def predict_diabetes(data: DiabetesInput):
    try:
        # Debug log
        print(f"Received prediction request for: {data.user_name}")
        
        # Encode categorical variables
        gender_encoded = gender_encoder.transform([data.gender.capitalize()])[0]
        smoking_encoded = smoking_encoder.transform([data.smoking_history])[0]

        # Create feature array
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
        
        # Scale features
        features_scaled = scaler.transform(features_raw)

        # Predict
        prediction = model.predict(features_scaled)[0]
        probability = model.predict_proba(features_scaled)[0].max()
        result_text = "Diabetic" if prediction == 1 else "Not Diabetic"

        # ✅ Return without database save
        return {
            "prediction": int(prediction),
            "probability": round(float(probability), 4),
            "result": result_text,
            "user_name": data.user_name,
            "saved": False,  # Indicates not saved to DB
            "message": "Database storage disabled on Vercel"
        }
        
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ✅ FIX 4: Add Mangum handler for Vercel
handler = Mangum(app)