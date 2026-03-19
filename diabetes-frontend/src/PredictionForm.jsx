import React, { useState } from 'react';

function PredictionForm() {
  const [formData, setFormData] = useState({
    gender: '',
    age: '',
    hypertension: '',
    heart_disease: '',
    smoking_history: '',
    bmi: '',
    hba1c_level: '',
    blood_glucose_level: ''
  });
  const [result, setResult] = useState(null);

  const handleChange = (e) => {
    setFormData({...formData, [e.target.name]: e.target.value});
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://127.0.0.1:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setResult({ error: err.toString() });
    }
  };

  return (
    <div>
      <h2>Diabetes Prediction</h2>
      <form onSubmit={handleSubmit}>
        <input name="gender" placeholder="Male/Female" onChange={handleChange} required />
        <input type="number" name="age" placeholder="Age" onChange={handleChange} required />
        <input type="number" name="hypertension" placeholder="Hypertension (0/1)" onChange={handleChange} required />
        <input type="number" name="heart_disease" placeholder="Heart Disease (0/1)" onChange={handleChange} required />
        <input name="smoking_history" placeholder="Smoking History" onChange={handleChange} required />
        <input type="number" step="0.1" name="bmi" placeholder="BMI" onChange={handleChange} required />
        <input type="number" step="0.1" name="hba1c_level" placeholder="HbA1c Level" onChange={handleChange} required />
        <input type="number" step="0.1" name="blood_glucose_level" placeholder="Blood Glucose Level" onChange={handleChange} required />
        <button type="submit">Predict</button>
      </form>
      {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  );
}

export default PredictionForm;
