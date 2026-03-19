import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import StandardScaler,LabelEncoder
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import classification_report , confusion_matrix,  roc_auc_score
from imblearn.over_sampling import SMOTE # imblearn = imbalanced-learn, a separate Python library
# built for handling imbalanced datasets.
# from imblearn.under_sampling import RandomUnderSampler
import joblib
import warnings
warnings.filterwarnings("ignore")
import seaborn as sns

data = pd.read_csv('diabetes_prediction_dataset.csv')

data.info()

data.describe()

# Combine former and not current
data['smoking_history'] = data['smoking_history'].replace({'former':'not current'})

# Create encoders
gender_encoder = LabelEncoder()
smoking_encoder = LabelEncoder()

data['gender'] = gender_encoder.fit_transform(data['gender'])
data['smoking_history'] = smoking_encoder.fit_transform(data['smoking_history'])

# Save encoders
joblib.dump(gender_encoder, "gender_encoder.pkl")
joblib.dump(smoking_encoder, "smoking_encoder.pkl")

features = ['gender', 'age', 'hypertension', 'heart_disease','smoking_history', 'bmi', 'HbA1c_level', 'blood_glucose_level']
Scaler = StandardScaler()
df_scaled = data.copy()
df_scaled[features] = Scaler.fit_transform(data[features])

# Save scaler AFTER it's fitted
joblib.dump(Scaler, "scaler.pkl")  # IMPORTANT: Save scaler for prediction

X = df_scaled[features]
Y = df_scaled['diabetes']

X_train, X_test, Y_train, Y_test = train_test_split(X, Y , test_size=0.2 , random_state=42)

model = XGBClassifier(
    n_estimators=200,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="logloss",
    random_state=42
)

model.fit(X_train, Y_train)
# assuming your trained model is called `model`
joblib.dump(model, "diabetes_model.pkl")
y_pred = model.predict(X_test)

print('Classification report')
print(classification_report(Y_test,y_pred))

conf_matrix = confusion_matrix(Y_test, y_pred)
plt.figure(figsize=(6,4))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues',
            xticklabels=Y.unique(), yticklabels=Y.unique())
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion matrix')
plt.tight_layout()
plt.show()

# SHapley Additive exPlanations, a method to explain ML predictions clearly and fairly.
# import shap
# explainer = shap.Explainer(model, X_train) # Creates an explainer object for your model.
# It learns how your model makes predictions using the training data (X_train).
# shap_values = explainer(X_test) # Computes SHAP values for the test data (X_test).
# SHAP value for a feature = how much that feature contributes to increasing or decreasing the prediction for each sample.

# shap.plots.bar(shap_values)

print('----Check you are Diabetic patient or not----')

try:
    # --- User inputs ---
    gender = str(input('Enter your Gender (Male/Female): ')).strip().upper()
    age = int(input('Enter Your age: '))
    hypertension = int(input('Enter Hypertension (0 or 1): '))
    heart_disease = int(input('Do you have Heart Disease? (0 or 1): '))
    smoking_history = str(input('Enter your Smoking History (never, current, not current, ever, No Info): '))
    bmi = float(input('Enter Body Mass Index: '))
    HbA1c_level = float(input('Enter HbA1c Level: '))
    blood_glucose_level = float(input('Enter Blood Glucose Level: '))

    # --- Create DataFrame ---
    user_input_df = pd.DataFrame([{
        'gender': gender,
        'age': age,
        'hypertension': hypertension,
        'heart_disease': heart_disease,
        'smoking_history': smoking_history,
        'bmi': bmi,
        'HbA1c_level': HbA1c_level,
        'blood_glucose_level': blood_glucose_level
    }])

    # --- Label Encoding for categorical columns ---
    # --- Label encode categorical columns ---
    Le = LabelEncoder()
    user_input_df['gender'] = Le.fit_transform(user_input_df['gender'])
    user_input_df['smoking_history'] = Le.fit_transform(user_input_df['smoking_history'])

    # --- Scale numerical features ---
    user_input_scaled = Scaler.transform(user_input_df)  # Scaler = already fitted StandardScaler or MinMaxScaler

    # --- Make prediction ---
    prediction = model.predict(user_input_scaled)[0]

    if prediction == 0:
        print('Prediction based on Patient data: You are Non-diabetic Patient')
    else:
        print('Prediction based on Patient data: You are Diabetic Patient')

except Exception as e:
    print("Error:", e)