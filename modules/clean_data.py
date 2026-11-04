import pandas as pd

# Load your dataset
df = pd.read_csv("EV_Range_Prediction_Dataset_2000.csv")

# Show missing values count
print("Missing values before cleaning:\n", df.isnull().sum())

# Drop any rows with missing or blank data
df_clean = df.dropna()

# Save the cleaned dataset back
df_clean.to_csv("EV_Range_Prediction_Dataset_2000.csv", index=False)
print("Dataset cleaned successfully! Remaining rows:", len(df_clean))