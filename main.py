from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
from pathlib import Path
import os

class Features(BaseModel):
    feature1: float = Field(..., description="First numeric feature")
    feature2: float = Field(..., description="Second numeric feature")

app = FastAPI(title="ML FastAPI on ECS", version="1.0.0")

MODEL_PATH = Path(__file__).parent / "model.joblib"

def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Model file not found. Run `python app/train.py` to create it.")
    return joblib.load(MODEL_PATH)

# Lazy load to speed container start
_model = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(features: Features):
    global _model
    if _model is None:
        _model = load_model()

    try:
        X = [[features.feature1, features.feature2]]
        y_pred = _model.predict(X)[0]
        return {"prediction": float(y_pred)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
