import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def calculate_linear_regression(df, lookback=2520):
    """Calcule une droite de régression sur les X derniers jours."""

    if len(df) < lookback:
        lookback = len(df)  # Si on a moins de données que lookback, on prend tout

    df_recent = df.iloc[-lookback:]  # On garde seulement les X dernières valeurs

    X = np.arange(len(df_recent)).reshape(-1, 1)  # Index des jours
    y = df_recent["Close"].values  # Prix de clôture

    if len(X) < 2:  # Vérification : impossible de faire une régression avec 1 seul point
        return np.array([]), 0

    model = LinearRegression()
    model.fit(X, y)

    regression_line = model.predict(X)  # Droite prédite
    slope = float(model.coef_[0])  # Convertir en float standard

    return regression_line.flatten(), slope


def calculate_standard_deviation(df, regression_line, lookback=2520):
    """Calcule l'écart type autour de la droite de régression et les niveaux ±1σ, ±2σ."""

    if len(df) < lookback:
        lookback = len(df)

    df_recent = df.iloc[-lookback:]  # Prend les X derniers jours

    # Calcul de l'écart type par rapport à la droite de régression
    residuals = df_recent["Close"] - regression_line  # Différences entre prix et droite
    std_dev = np.std(residuals)  # Écart type des résidus

    levels = {
        "+1σ": regression_line + std_dev,
        "-1σ": regression_line - std_dev,
        "+2σ": regression_line + 2 * std_dev,
        "-2σ": regression_line - 2 * std_dev,
    }

    return std_dev, levels

