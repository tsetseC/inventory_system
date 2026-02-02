import os
import joblib
import pandas as pd

MODEL_PATH = os.path.join("ml", "kaggle_demand_model.pkl")

# Load model
model = joblib.load(MODEL_PATH)

def predict_demand(input_data: dict):
    """
    input_data must include fields found in the Kaggle dataset:
    'Store_ID', 'Product_ID', 'Category', 'Region', 'Inventory_Level',
    'Units_Ordered', 'Demand_Forecast', 'Price', 'Discount',
    'Weather_Condition', 'Holiday_Promotion', 'Competitor_Pricing',
    'Seasonality', 'Date'
    """

    df = pd.DataFrame([input_data])

    # Date features
    df["Date"] = pd.to_datetime(df["Date"])
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["Day"] = df["Date"].dt.day
    df["DayOfWeek"] = df["Date"].dt.dayofweek

    df = df.drop(columns=["Date"])

    # Run model
    prediction = model.predict(df)[0]

    return round(float(prediction), 2)
