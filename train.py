import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib

# Load your dataset
df = pd.read_csv("EV_Range_Prediction_Dataset_2000.csv")

# Select features and target, and force conversion to numeric to prevent string errors
feature_cols = ['distance_traveled', 'temperature', 'speed', 'vehicle_load']
target_col = 'power_consumption'

for col in feature_cols + [target_col]:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Drop any rows that failed conversion or contain missing values
df = df.dropna(subset=feature_cols + [target_col])

X = df[feature_cols]
y = df[target_col]

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train the Random Forest model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save the trained model artifact
joblib.dump(model, 'ev_rf_model.pkl')
print("Model trained and saved successfully as ev_rf_model.pkl!")