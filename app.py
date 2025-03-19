import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.data_fetcher import fetch_stock_data, get_stock_suggestions
from utils.indicators import calculate_linear_regression, calculate_standard_deviation

# Configuration de la page Streamlit
st.set_page_config(page_title="Finance Dashboard", layout="wide")

# Sidebar : Sélection de l'action avec une barre de recherche dynamique
st.sidebar.title("Sélection de l'actif")
query = st.sidebar.text_input("Tapez le nom ou le ticker d'une action")
stock_list = get_stock_suggestions(query) if query else []
selected_stock = st.sidebar.selectbox("Choisissez une action", stock_list) if stock_list else None

# Sélection de la période
timeframe = st.sidebar.selectbox("Choisissez la période", ["Daily", "Weekly", "Monthly"])
interval_mapping = {"Daily": "1d", "Weekly": "1wk", "Monthly": "1mo"}

# Sélection des indicateurs
indicators = st.sidebar.multiselect("Indicateurs", ["Linear Regression", "Standard Deviation", "Market Linear Regression"])

if selected_stock:
    # Récupération des données
    df = fetch_stock_data(selected_stock, interval_mapping[timeframe])

    if not df.empty:
        # Sélection de la période pour la régression linéaire
        lookback = st.sidebar.slider(
            "Période de régression (nombre de jours)",
            min_value=500,  # Minimum ≈ 2 ans
            max_value=len(df),  # Max = tout l'historique récupéré
            value=min(2520, len(df)),  # Valeur par défaut ≈ 10 ans (mais pas plus que dispo)
            step=250
        )

        # Création du graphique interactif
        fig = go.Figure()

        # Ajout des prix
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="Prix"
        ))

        # Ajout des indicateurs sélectionnés
        regression_line, slope = None, None

        if "Linear Regression" in indicators:
            regression_line, slope = calculate_linear_regression(df, lookback)

            if regression_line.size > 0:  # Vérifier qu'on a bien une régression valide
                fig.add_trace(go.Scatter(
                    x=df.index[-lookback:],
                    y=regression_line,
                    mode="lines",
                    name="Linear Regression",
                    line=dict(dash="dash")
                ))
                st.sidebar.write(f"Pente de la droite de régression : {slope:.5f}")
            else:
                st.sidebar.write("Pas assez de données pour calculer la régression.")

        if "Standard Deviation" in indicators and regression_line is not None:
            std_dev, levels = calculate_standard_deviation(df, regression_line, lookback)

            if std_dev > 0:
                for level, value in levels.items():
                    fig.add_trace(go.Scatter(
                        x=df.index[-lookback:],
                        y=value,
                        mode="lines",
                        name=f"Std Dev {level}",
                        line=dict(dash="dot")
                    ))
                st.sidebar.write(f"Écart type : {std_dev:.5f}")
            else:
                st.sidebar.write("Pas assez de données pour calculer l'écart type.")

        # Ajout d'options interactives
        fig.update_layout(title=f"{selected_stock} - {timeframe}",
                          xaxis_title="Date",
                          yaxis_title="Prix",
                          xaxis_rangeslider_visible=False)

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Impossible de récupérer les données de l'action sélectionnée.")
