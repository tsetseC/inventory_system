import os
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "..", "ml", "kaggle_demand_model.pkl")


def load_model():
    """
    Load ML model safely.
    If missing, return None instead of crashing deployment.
    """
    if not os.path.exists(MODEL_PATH):
        print(f"[WARNING] ML model not found at: {MODEL_PATH}")
        return None

    try:
        return joblib.load(MODEL_PATH)
    except Exception as e:
        print(f"[ERROR] Failed to load ML model: {e}")
        return None


MODEL = load_model()


def predict_demand(features):
    """
    Predict demand safely.
    If MODEL is missing, return fallback result.
    """
    if MODEL is None:
        return {
            "prediction": None,
            "status": "Model not available on server (missing file)."
        }

    try:
        pred = MODEL.predict([features])[0]
        return {
            "prediction": float(pred),
            "status": "Prediction successful"
        }
    except Exception as e:
        return {
            "prediction": None,
            "status": f"Prediction failed: {str(e)}"
        }
