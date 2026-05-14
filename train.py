import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import os

# Load dataset
df = pd.read_csv('data/ai4i2020.csv')

# Preprocessing
# Drop UDI and Product ID
df = df.drop(['UDI', 'Product ID'], axis=1)

# Rename columns to remove brackets for XGBoost
df.columns = [c.replace('[', '').replace(']', '').replace('<', '') for c in df.columns]

# Encode 'Type'
le = LabelEncoder()
df['Type'] = le.fit_transform(df['Type'])
joblib.dump(le, 'models/type_encoder.joblib')

# Synthesize RUL
# Assuming max tool wear is 250 mins.
# If a failure occurs, we'll say RUL is 0 for simplicity in this snapshot.
df['RUL'] = 250 - df['Tool wear min']
df.loc[df['Machine failure'] == 1, 'RUL'] = 0
df['RUL'] = df['RUL'].clip(lower=0)

# Features and Targets
X = df.drop(['Machine failure', 'TWF', 'HDF', 'PWF', 'OSF', 'RNF', 'RUL'], axis=1)
y_class = df['Machine failure']
y_reg = df['RUL']

# Split data
X_train, X_test, y_class_train, y_class_test, y_reg_train, y_reg_test = train_test_split(
    X, y_class, y_reg, test_size=0.2, random_state=42
)

# Train Classification Model (Failure Prediction)
clf = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
clf.fit(X_train, y_class_train)
joblib.dump(clf, 'models/failure_classifier.joblib')

# Train Regression Model (RUL Estimation)
reg = xgb.XGBRegressor(objective='reg:squarederror', random_state=42)
reg.fit(X_train, y_reg_train)
joblib.dump(reg, 'models/rul_regressor.joblib')

print("Models trained and saved successfully.")
print(f"Features used: {list(X.columns)}")
