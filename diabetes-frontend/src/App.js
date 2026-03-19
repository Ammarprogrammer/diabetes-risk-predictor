import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import "./App.css";

function App() {
  const initialForm = {
    user_name: "",
    gender: "Male",
    age: 30,
    hypertension: 0,
    heart_disease: 0,
    smoking_history: "never",
    bmi: 25,
    hba1c_level: 5.5,
    blood_glucose_level: 100
  };

  const [formData, setFormData] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [userHistory, setUserHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.user_name.trim()) {
      alert("Please enter your name");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...formData,
          age: parseInt(formData.age),
          hypertension: parseInt(formData.hypertension),
          heart_disease: parseInt(formData.heart_disease),
          bmi: parseFloat(formData.bmi),
          hba1c_level: parseFloat(formData.hba1c_level),
          blood_glucose_level: parseInt(formData.blood_glucose_level)
        })
      });
      
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || `API Error: ${res.status}`);
      }
      
      const data = await res.json();
      setResult(data);
      if (data.saved) {
        fetchUserHistory(formData.user_name);
      }
    } catch (err) {
      console.error("Full error:", err);
      alert(`Error: ${err.message || 'Could not connect to API. Make sure backend is running on http://127.0.0.1:8000'}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserHistory = async (userName) => {
    setHistoryLoading(true);
    try {
      const res = await fetch(`http://127.0.0.1:8000/predictions/${encodeURIComponent(userName)}`);
      if (!res.ok) throw new Error(`Failed to fetch: ${res.status}`);
      const data = await res.json();
      setUserHistory(data.predictions || []);
    } catch (err) {
      console.error("Error fetching history:", err);
      alert(`Could not fetch history: ${err.message}`);
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleReset = () => {
    setFormData(initialForm);
    setResult(null);
  };

  const loadHistory = () => {
    if (formData.user_name.trim()) {
      setShowHistory(!showHistory);
      if (!showHistory) {
        fetchUserHistory(formData.user_name);
      }
    } else {
      alert("Please enter your name first");
    }
  };

  return (
    <div className="App">
      <motion.h1
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1 }}
      >
        Diabetes Prediction
      </motion.h1>

      <motion.form
        onSubmit={handleSubmit}
        className="form-container"
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1 }}
      >
        <label>Name:</label>
        <input 
          type="text" 
          name="user_name" 
          placeholder="Enter your name" 
          value={formData.user_name} 
          onChange={handleChange}
          required
        />

        <label>Gender:</label>
        <select name="gender" value={formData.gender} onChange={handleChange}>
          <option value="Male">♂ Male</option>
          <option value="Female">♀ Female</option>
        </select>

        <label>Age:</label>
        <input type="number" name="age" min="0" max="120" value={formData.age} onChange={handleChange} />

        <label>Hypertension:</label>
        <select name="hypertension" value={formData.hypertension} onChange={handleChange}>
          <option value={0}>No</option>
          <option value={1}>Yes</option>
        </select>

        <label>Heart Disease:</label>
        <select name="heart_disease" value={formData.heart_disease} onChange={handleChange}>
          <option value={0}>No</option>
          <option value={1}>Yes</option>
        </select>

        <label>Smoking History:</label>
        <select name="smoking_history" value={formData.smoking_history} onChange={handleChange}>
          <option value="never">Never</option>
          <option value="current">Current</option>
          <option value="not current">Not Current</option>
          <option value="ever">Ever</option>
          <option value="No Info">No Info</option>
        </select>

        <label>BMI:</label>
        <input type="number" name="bmi" min="10" max="50" step="0.1" value={formData.bmi} onChange={handleChange} />

        <label>HbA1c Level (%):</label>
        <input type="number" name="hba1c_level" min="4" max="14" step="0.1" value={formData.hba1c_level} onChange={handleChange} />
        {formData.hba1c_level > 12 && <p className="warning pulse">⚠ HbA1c very high!</p>}

        <label>Blood Glucose Level (mg/dL):</label>
        <input type="number" name="blood_glucose_level" min="50" max="400" value={formData.blood_glucose_level} onChange={handleChange} />
        {formData.blood_glucose_level > 300 && <p className="warning pulse">⚠ Blood Glucose very high!</p>}

        <button type="submit" className="submit-btn" disabled={loading}>
          {loading ? "Predicting..." : "Predict"}
        </button>
      </motion.form>

      <AnimatePresence>
        {result && (
          <motion.div
            key={result.result}
            initial={{ opacity: 0, x: 200 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -200 }}
            transition={{ type: "spring", stiffness: 80 }}
            className={`result ${result.result === "Diabetic" ? "diabetic" : "not-diabetic"}`}
          >
            <h2>Prediction: {result.result}</h2>
            <p>Probability: {(result.probability * 100).toFixed(2)}%</p>
            <div className="probability-bar">
              <div className="filled-bar" style={{ width: `${result.probability * 100}%` }}></div>
            </div>
            <p className="saved-message">✓ Data saved successfully</p>
            <button onClick={handleReset} className="reset-btn">Predict Again</button>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.button
        onClick={loadHistory}
        className="history-btn"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        {showHistory ? "Hide History" : "View Prediction History"}
      </motion.button>

      <AnimatePresence>
        {showHistory && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="history-container"
          >
            <h2>Prediction History for {formData.user_name}</h2>
            {historyLoading ? (
              <p>Loading history...</p>
            ) : userHistory.length === 0 ? (
              <p>No predictions yet</p>
            ) : (
              <div className="history-list">
                {userHistory.map((record, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className={`history-item ${record.result === "Diabetic" ? "diabetic-history" : "not-diabetic-history"}`}
                  >
                    <p><strong>Date:</strong> {new Date(record.created_at).toLocaleString()}</p>
                    <p><strong>Result:</strong> {record.result}</p>
                    <p><strong>Probability:</strong> {(record.probability * 100).toFixed(2)}%</p>
                    <p><strong>Age:</strong> {record.age}</p>
                  </motion.div>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;
