import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import joblib


def main():
    # -------------------------------------------------
    # 1. Load CSV
    # -------------------------------------------------
    df = pd.read_csv("data/retail_store_inventory.csv")
    print("✅ Dataset loaded:", df.shape)
    print(df.head())

    # -------------------------------------------------
    # 2. Clean column names
    #    - strip spaces
    #    - replace spaces and "/" with "_"
    # -------------------------------------------------
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("/", "_")
    )

    print("\n🔤 Cleaned columns:", df.columns.tolist())

    # Columns after cleaning should be:
    # ['Date', 'Store_ID', 'Product_ID', 'Category', 'Region',
    #  'Inventory_Level', 'Units_Sold', 'Units_Ordered',
    #  'Demand_Forecast', 'Price', 'Discount',
    #  'Weather_Condition', 'Holiday_Promotion',
    #  'Competitor_Pricing', 'Seasonality']

    # -------------------------------------------------
    # 3. Date parsing + time features
    # -------------------------------------------------
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["Day"] = df["Date"].dt.day
    df["DayOfWeek"] = df["Date"].dt.dayofweek  # 0=Mon, 6=Sun

    # We don’t need the raw Date anymore for the model
    df = df.drop(columns=["Date"])

    # -------------------------------------------------
    # 4. Fix bad values in Demand_Forecast
    #    (there are -9.99 values which are clearly noise)
    # -------------------------------------------------
    if "Demand_Forecast" in df.columns:
        df["Demand_Forecast"] = df["Demand_Forecast"].clip(lower=0)

    # -------------------------------------------------
    # 5. Define target + feature columns
    # -------------------------------------------------
    target_col = "Units_Sold"

    feature_cols = [
        "Inventory_Level",
        "Units_Ordered",
        "Demand_Forecast",
        "Price",
        "Discount",
        "Holiday_Promotion",
        "Competitor_Pricing",
        "Seasonality",
        "Weather_Condition",
        "Category",
        "Region",
        "Store_ID",
        "Product_ID",
        "Year",
        "Month",
        "Day",
        "DayOfWeek",
    ]

    X = df[feature_cols]
    y = df[target_col]

    # -------------------------------------------------
    # 6. Identify categorical vs numeric features
    # -------------------------------------------------
    categorical_cols = [
        "Seasonality",
        "Weather_Condition",
        "Category",
        "Region",
        "Store_ID",
        "Product_ID",
    ]

    numeric_cols = [c for c in feature_cols if c not in categorical_cols]

    print("\n📊 Numeric features:", numeric_cols)
    print("🔠 Categorical features:", categorical_cols)

    # -------------------------------------------------
    # 7. Build preprocessing pipelines
    # -------------------------------------------------
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocess = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_cols),
            ("cat", categorical_transformer, categorical_cols),
        ]
    )

    # -------------------------------------------------
    # 8. Full model pipeline (preprocess + regressor)
    # -------------------------------------------------
    model = Pipeline(
        steps=[
            ("preprocess", preprocess),
            ("regressor", RandomForestRegressor(
                n_estimators=200,
                random_state=42,
                n_jobs=-1,
            )),
        ]
    )

    # -------------------------------------------------
    # 9. Train / test split
    # -------------------------------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print("\n📦 Training set:", X_train.shape, "  🧪 Test set:", X_test.shape)

    # -------------------------------------------------
    # 10. Train the model
    # -------------------------------------------------
    print("\n🚀 Training model...")
    model.fit(X_train, y_train)

    # -------------------------------------------------
    # 11. Evaluate
    # -------------------------------------------------
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)

    print(f"\n✅ Model trained successfully!")
    print(f"📉 Mean Absolute Error (MAE) on test set: {mae:.3f}")

    # -------------------------------------------------
    # 12. Save the trained pipeline
    # -------------------------------------------------
    output_path = "ml/kaggle_demand_model.pkl"
    joblib.dump(model, output_path)
    print(f"\n💾 Model pipeline saved to: {output_path}")


if __name__ == "__main__":
    main()
