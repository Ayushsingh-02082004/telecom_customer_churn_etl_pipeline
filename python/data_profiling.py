from pathlib import Path
import pandas as pd

# Automatically resolves to the project root directory
BASE_DIR = Path(__file__).resolve().parent.parent
file_path = BASE_DIR / "data" / "raw" / "telco_customer_churn.csv"

df = pd.read_csv(file_path)

print(df.head())
print(df.shape)
print(df.columns)


print("\nShape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nData Types:")
print(df.dtypes)

print("\nMissing Values:")
print(df.isnull().sum())

print("\nDuplicate Rows:")
print(df.duplicated().sum())


for column in df.columns:
    print(f"\n--- {column} ---")
    print(df[column].unique()[:20])


print(df[[
    "tenure",
    "MonthlyCharges",
    "TotalCharges"
]].describe())


print(df["Churn"].value_counts())

print("\nChurn percentage:")
print(df["Churn"].value_counts(normalize=True) * 100)


# Total count of missing values
print("Missing in TotalCharges:", df["TotalCharges"].isnull().sum())

