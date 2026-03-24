import pandas as pd

df = pd.read_csv("data/E0.csv")
columns_to_keep = [
    "Date",
    "HomeTeam",
    "AwayTeam",
    "FTHG",
    "FTAG",
    "HS",
    "AS",
    "HST",
    "AST",
    "HC",
    "AC",
    "HY",
    "AY",
    "HR",
    "AR"
]

df_clean = df[columns_to_keep]

df_clean.to_csv("EPL_clean.csv", index=False)

print(df_clean.head())