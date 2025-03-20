import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def calculate_linear_regression(df, lookback=520):
    """Calcule une droite de régression sur les X dernières semaines avec une pente correcte en %."""
    if len(df) < lookback:
        lookback = len(df)

    df_recent = df.iloc[-lookback:]
    X = np.arange(len(df_recent)).reshape(-1, 1)  # Index des semaines
    y = df_recent["Close"].values  # Prix de clôture

    if len(X) < 2:
        return np.array([]), 0

    model = LinearRegression()
    model.fit(X, y)

    regression_line = model.predict(X)
    slope_raw = float(model.coef_[0])  # Pente brute en prix/semaine

    # 🔥 **Correction : Conversion en % de croissance hebdomadaire**
    initial_value = regression_line[0]  # Prix au début de la régression
    slope_percentage = (slope_raw / initial_value) * 100  # Pente en % par semaine

    return regression_line.flatten(), slope_percentage

def calculate_standard_deviation(df, regression_line, lookback=520):
    """Calcule l'écart type autour de la droite de régression et les niveaux ±1σ, ±2σ."""
    if len(df) < lookback:
        lookback = len(df)

    df_recent = df.iloc[-lookback:]

    residuals = df_recent["Close"] - regression_line
    std_dev = np.std(residuals)

    levels = {
        "+1σ": regression_line + std_dev,
        "-1σ": regression_line - std_dev,
        "+2σ": regression_line + 2 * std_dev,
        "-2σ": regression_line - 2 * std_dev,
        "+3σ": regression_line + 3 * std_dev,
        "-3σ": regression_line - 3 * std_dev,

    }

    return std_dev, levels

def calculate_sma(df):
    """Calcule la SMA 50 et SMA 200."""
    sma_50 = df["Close"].rolling(window=50).mean()
    sma_200 = df["Close"].rolling(window=200).mean()
    return sma_50, sma_200

def calculate_rsi(df, period=14):
    """Calcule le RSI (Relative Strength Index).""" # Recalculer le RSI
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
