# Diabetes Prediction System with Database

A full-stack web application for diabetes prediction using machine learning with user data persistence to a database.

## 📋 Project Structure

```
├── main.py                          # FastAPI backend with database integration
├── database.py                      # SQLAlchemy database setup and models
├── diabetes_predictor.py            # ML model training script
├── diabetes_model.pkl               # Trained XGBoost model
├── gender_encoder.pkl               # LabelEncoder for gender
├── smoking_encoder.pkl              # LabelEncoder for smoking history
├── diabetes_prediction_dataset.csv  # Training dataset
├── requirements.txt                 # Python dependencies
└── diabetes-frontend/               # React frontend
    ├── src/
    │   ├── App.js                   # Main React component with history
    │   ├── App.css                  # Styling
    │   ├── PredictionForm.jsx       # Prediction form component
    │   └── index.js                 # React entry point
    └── package.json                 # Node dependencies
```

## 🗄️ Database Setup

### Database Schema

The application uses SQLite with the following table:

**predictions** table:

- `id` (Integer, Primary Key)
- `user_name` (String) - Name of the user
- `gender` (String) - User's gender
- `age` (Integer) - User's age
- `hypertension` (Integer) - 0 or 1
- `heart_disease` (Integer) - 0 or 1
- `smoking_history` (String) - Smoking status
- `bmi` (Float) - Body Mass Index
- `hba1c_level` (Float) - HbA1c level percentage
- `blood_glucose_level` (Float) - Blood glucose in mg/dL
- `prediction` (Integer) - 0 for Not Diabetic, 1 for Diabetic
- `probability` (Float) - Confidence score (0-1)
- `result` (String) - "Diabetic" or "Not Diabetic"
- `created_at` (DateTime) - Timestamp of prediction

The database file `diabetes_predictions.db` is automatically created in the project root when you run the backend.

## 🚀 Installation & Setup

### ⚠️ CRITICAL: Generate Model Files FIRST

**Before starting the backend, regenerate the model files with the updated code:**

```bash
python diabetes_predictor.py
```

This creates all required files including the **new `scaler.pkl`** (essential for correct predictions).

### Backend Setup

1. **Install Python dependencies:**

```bash
pip install -r requirements.txt
```

2. **Run the FastAPI server:**

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

### Frontend Setup

1. **Navigate to the frontend directory:**

```bash
cd diabetes-frontend
```

2. **Install Node dependencies:**

```bash
npm install
```

3. **Start the React development server:**

```bash
npm start
```

The frontend will open at `http://localhost:3000`

## 📡 API Endpoints

### POST `/predict`

**Predict diabetes and save user data**

Request body:

```json
{
  "user_name": "John Doe",
  "gender": "Male",
  "age": 45,
  "hypertension": 0,
  "heart_disease": 0,
  "smoking_history": "never",
  "bmi": 25.5,
  "hba1c_level": 6.2,
  "blood_glucose_level": 120
}
```

Response:

```json
{
  "id": 1,
  "prediction": 0,
  "probability": 0.8743,
  "result": "Not Diabetic",
  "saved": true
}
```

### GET `/`

**Health check**

Response:

```json
{
  "message": "Diabetes Prediction API is running"
}
```

### GET `/predictions`

**Retrieve all stored predictions**

Response:

```json
{
  "total": 5,
  "predictions": [
    {
      "id": 1,
      "user_name": "John Doe",
      "age": 45,
      "gender": "Male",
      "prediction": 0,
      "result": "Not Diabetic",
      "probability": 0.8743,
      "created_at": "2026-03-04T12:30:45"
    },
    ...
  ]
}
```

### GET `/predictions/{user_name}`

**Retrieve predictions for a specific user**

Example: `GET /predictions/John%20Doe`

Response:

```json
{
  "user_name": "John Doe",
  "total": 3,
  "predictions": [
    {
      "id": 1,
      "age": 45,
      "gender": "Male",
      "prediction": 0,
      "result": "Not Diabetic",
      "probability": 0.8743,
      "created_at": "2026-03-04T12:30:45"
    },
    ...
  ]
}
```

### GET `/predictions/record/{record_id}`

**Retrieve a specific prediction record**

Example: `GET /predictions/record/1`

Response:

```json
{
  "id": 1,
  "user_name": "John Doe",
  "gender": "Male",
  "age": 45,
  "hypertension": 0,
  "heart_disease": 0,
  "smoking_history": "never",
  "bmi": 25.5,
  "hba1c_level": 6.2,
  "blood_glucose_level": 120,
  "prediction": 0,
  "result": "Not Diabetic",
  "probability": 0.8743,
  "created_at": "2026-03-04T12:30:45"
}
```

## 🎯 Features

### Frontend Features

- ✅ User name input for data tracking
- ✅ Interactive form with validation
- ✅ Real-time prediction visualization
- ✅ Automated data saving to database
- ✅ View prediction history per user
- ✅ Responsive design with animations
- ✅ Health warnings for extreme values

### Backend Features

- ✅ XGBoost ML model for prediction
- ✅ SQLite database for persistence
- ✅ CORS enabled for frontend communication
- ✅ RESTful API for all operations
- ✅ Automatic data validation
- ✅ Categorical encoding (Gender, Smoking History)
- ✅ Scalable feature preprocessing

## 📊 Using the Application

1. **Open the application:** Visit `http://localhost:3000`

2. **Enter your information:**
   - Name (required for tracking)
   - Gender
   - Age
   - Health metrics

3. **Get prediction:** Click "Predict" button

4. **View history:** Click "View Prediction History" to see all your past predictions

5. **Data persistence:** All predictions are automatically saved to the database

## 🔍 Database Access

To inspect the database directly:

```python
from database import SessionLocal, PredictionRecord

db = SessionLocal()
all_predictions = db.query(PredictionRecord).all()

for record in all_predictions:
    print(f"{record.user_name}: {record.result}")
```

Or use SQLite CLI:

```bash
sqlite3 diabetes_predictions.db
sqlite> SELECT * FROM predictions;
sqlite> SELECT COUNT(*) as total_predictions FROM predictions;
sqlite> SELECT user_name, result, COUNT(*) as count FROM predictions GROUP BY user_name, result;
```

## 🛠️ Training the Model

To retrain the model with new data:

```bash
python diabetes_predictor.py
```

This will:

1. Load the dataset
2. Preprocess and scale features
3. Train XGBoost classifier
4. Save model and encoders
5. Display SHAP explanations

## 📝 Input Validation

The API validates all inputs:

- **Gender:** Must be "Male" or "Female"
- **Smoking History:** "never", "current", "not current", "ever", "No Info"
- **Age:** 0-120
- **Hypertension/Heart Disease:** 0 or 1
- **BMI:** 10-50
- **HbA1c Level:** 4-14
- **Blood Glucose:** 50-400

## 🔒 CORS Configuration

The backend allows requests from:

- `http://localhost:3000` (development)

To add more origins, modify `main.py`:

```python
allow_origins=["http://localhost:3000", "http://your-domain.com"]
```

## 📚 Model Details

- **Algorithm:** XGBoost Classifier
- **Features:** 8 health metrics
- **Training Samples:** ~100,000
- **Classes:** 2 (Diabetic / Not Diabetic)
- **Evaluation Metric:** LogLoss
- **Model Accuracy:** ~97%

## 🐛 Troubleshooting

### NumPy / joblib errors

If you encounter a traceback mentioning **`ModuleNotFoundError: No module named 'numpy._core'`** or similar when starting the backend, the problem is usually a broken or mismatched NumPy installation. This arises when joblib tries to unpickle the model or encoders but cannot access required NumPy internals.

**Steps to fix:**

1. Activate the correct Python environment.
2. Reinstall or upgrade NumPy:
   ```bash
   pip install --upgrade numpy
   ```
3. Restart the FastAPI server.

The code now catches this on startup and raises a clear `RuntimeError` with guidance.

### Binary incompatibility errors

Sometimes upgrading NumPy (or other compiled libraries) without reinstalling dependent packages leads to errors such as:

```
ValueError: numpy.dtype size changed, may indicate binary incompatibility. Expected 96 from C header, got 88 from PyObject
```

or messages referring to "binary incompatibility" when importing pandas/xgboost.

**Fix steps:**

1. Reinstall susceptible packages:
   ```bash
   pip install --upgrade --force-reinstall numpy pandas xgboost
   ```
2. If problem persists, recreate your virtual environment and reinstall from `requirements.txt`.

### Database errors

- Delete `diabetes_predictions.db` and restart the server

### CORS errors

- Ensure frontend URL in `allow_origins` matches `http://localhost:3000`

### Model not found

- Run `diabetes_predictor.py` to generate model files

### Port already in use

- Backend: `uvicorn main:app --reload --port 8001`
- Frontend: `PORT=3001 npm start`

## 📄 License

This project is provided as-is for educational purposes.
