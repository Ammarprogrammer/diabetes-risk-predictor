# Quick Start Guide - Diabetes Prediction System with Database

## 🚀 Quick Setup (5 minutes)

### Option 1: Automated Setup (Windows)

```bash
setup.bat
```

### Option 2: Manual Setup

**Step 1: Install Backend Dependencies**

```bash
pip install -r requirements.txt
```

**Step 2: Install Frontend Dependencies**

```bash
cd diabetes-frontend
npm install
cd ..
```

**Step 3: Start Backend (Terminal 1)**

```bash
uvicorn main:app --reload
```

✅ Backend running at: `http://127.0.0.1:8000`

**Step 4: Start Frontend (Terminal 2)**

```bash
cd diabetes-frontend
npm start
```

✅ Frontend running at: `http://localhost:3000`

## 📊 What's New: Database Integration

### ✅ Database Created Automatically

- File: `diabetes_predictions.db` (SQLite)
- Created on first API call
- Stores all user predictions

### ✅ All Predictions Are Saved

When you click "Predict", the data is automatically:

1. Sent to backend
2. Processed by ML model
3. **Saved to database with:**
   - User name
   - All health metrics
   - Prediction result
   - Confidence score
   - Timestamp

### ✅ View Your Prediction History

- Click "View Prediction History" button
- See all your past predictions
- Organized by date
- Shows success rate

## 📱 Using the Application

1. **Enter your name** (required for tracking)
2. **Fill health information** (age, BMI, glucose, etc.)
3. **Click Predict** → Instant result + Auto-saved
4. **View History** → See all your past predictions

## 🔍 Check Stored Data

### From Python

```python
from database import SessionLocal, PredictionRecord

db = SessionLocal()
for record in db.query(PredictionRecord).all():
    print(f"{record.user_name}: {record.result}")
```

### From Command Line (SQLite)

```bash
sqlite3 diabetes_predictions.db
> SELECT * FROM predictions;
> SELECT COUNT(*) FROM predictions;
```

## 📡 API Endpoints

```
POST   http://127.0.0.1:8000/predict              # Make prediction + save
GET    http://127.0.0.1:8000/predictions          # Get all predictions
GET    http://127.0.0.1:8000/predictions/John     # Get user's predictions
GET    http://127.0.0.1:8000/predictions/record/1 # Get specific record
```

## ⚙️ Configuration

### Change Frontend Port

```bash
PORT=3001 npm start
```

### Change Backend Port

```bash
uvicorn main:app --reload --port 8001
```

### Add More Allowed Origins (other domains)

In `main.py`, line 13:

```python
allow_origins=["http://localhost:3000", "http://your-domain.com"]
```

## 🗄️ Database Tables

**predictions** table with columns:

- user_name, gender, age
- hypertension, heart_disease, smoking_history
- bmi, hba1c_level, blood_glucose_level
- prediction (0/1), result, probability
- created_at (timestamp)

## 🛠️ Troubleshooting

| Problem              | Solution                                          |
| -------------------- | ------------------------------------------------- |
| Database error       | Delete `diabetes_predictions.db`, restart backend |
| CORS error           | Ensure frontend at `http://localhost:3000`        |
| Model not found      | Run `python diabetes_predictor.py`                |
| Port in use          | Use different port: `--port 8001`                 |
| Dependencies missing | Run `pip install -r requirements.txt`             |

## 📚 Files Modified/Created

```
✅ database.py           # NEW - Database setup & models
✅ main.py              # UPDATED - Backend with DB operations
✅ App.js               # UPDATED - Frontend with history feature
✅ App.css              # UPDATED - New styling for history
✅ requirements.txt     # NEW - Python dependencies
✅ DATABASE_README.md   # NEW - Detailed documentation
✅ setup.bat            # NEW - Automated Windows setup
✅ QUICK_START.md       # NEW - This file
```

## 🎯 Key Features Now Available

✅ **User Data Persistence** - Never lose prediction history  
✅ **Per-User Tracking** - View your prediction timeline  
✅ **Automatic Saving** - No extra clicks needed  
✅ **Clean History UI** - See past results at a glance  
✅ **Timestamp Recording** - Know when predictions were made  
✅ **Full Data Storage** - All metrics stored for analysis

## 📞 Support

- Check `DATABASE_README.md` for detailed docs
- Review API endpoints section above
- Inspect database with SQLite CLI
- Check browser console for frontend errors
- Check terminal for backend errors

---

**Ready?** Start the backend and frontend, open http://localhost:3000 and begin! 🎉
