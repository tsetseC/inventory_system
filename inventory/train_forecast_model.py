import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from joblib import dump

csv_path = Path("inventory/data/rfid_demand_ml.csv")
df = pd.read_csv(csv_path)

X = df.drop(columns=["date", "sales"])
y = df["sales"]

model = RandomForestRegressor(
    n_estimators=300,
    random_state=42,
    max_depth=10
)
model.fit(X, y)

model_path = Path("inventory/models/rfid_forecast_model.joblib")
model_path.parent.mkdir(exist_ok=True)
dump(model, model_path)

print(f"Model saved to: {model_path}")
