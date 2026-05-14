from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np

app = FastAPI(title="PdM Prediction API")

# Load models and encoder
try:
    classifier = joblib.load('models/failure_classifier.joblib')
    regressor = joblib.load('models/rul_regressor.joblib')
    type_encoder = joblib.load('models/type_encoder.joblib')
except Exception as e:
    print(f"Error loading models: {e}")

class SensorData(BaseModel):
    Type: str
    Air_temperature: float
    Process_temperature: float
    Rotational_speed: float
    Torque: float
    Tool_wear: float

@app.get("/")
def read_root():
    return {"message": "Predictive Maintenance API is running"}

@app.post("/predict")
def predict(data: SensorData):
    try:
        # Prepare data for prediction
        # Map input names to model feature names
        # Features used: ['Type', 'Air temperature K', 'Process temperature K', 'Rotational speed rpm', 'Torque Nm', 'Tool wear min']

        input_df = pd.DataFrame([{
            'Type': type_encoder.transform([data.Type])[0],
            'Air temperature K': data.Air_temperature,
            'Process temperature K': data.Process_temperature,
            'Rotational speed rpm': data.Rotational_speed,
            'Torque Nm': data.Torque,
            'Tool wear min': data.Tool_wear
        }])

        failure_prob = float(classifier.predict_proba(input_df)[0][1])
        failure_pred = int(classifier.predict(input_df)[0])
        rul_pred = float(regressor.predict(input_df)[0])

        return {
            "failure_probability": failure_prob,
            "failure_prediction": failure_pred,
            "estimated_rul": max(0, rul_pred)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
