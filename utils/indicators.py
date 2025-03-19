import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def calculate_linear_regression(df):
    """Calcule la droite de régression linéaire et retourne sa pente."""
    df = df.reset_index()
    df["Timestamp"] = df["Date"].astype(np.int64) // 10**9  # Conversion de la date en timestamp

    X = df["Timestamp"].values.reshape(-1, 1)
    y = df["Close"].values.reshape(-1, 1)

    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)
    slope = model.coef_[0][0]

    return y_pred.flatten(), slope

def calculate_standard_deviation(df):
    """Calcule l'écart type et les niveaux 1σ, 2σ, 3σ autour du prix moyen."""
    mean_price = df["Close"].mean()
    std_dev = df["Close"].std()

    levels = {
        "+1σ": mean_price + std_dev,
        "-1σ": mean_price - std_dev,
        "+2σ": mean_price + 2*std_dev,
        "-2σ": mean_price - 2*std_dev,
        "+3σ": mean_price + 3*std_dev,
        "-3σ": mean_price - 3*std_dev,
    }
    return std_dev, levels
