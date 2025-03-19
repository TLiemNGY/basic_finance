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
query = st.sidebar.text_input("Tapez le nom d'une action")
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
        if "Linear Regression" in indicators:
            regression_line, slope = calculate_linear_regression(df)
            fig.add_trace(go.Scatter(x=df.index, y=regression_line, mode="lines", name="Linear Regression", line=dict(dash="dash")))
            st.sidebar.write(f"Pente de la droite de régression : {slope:.5f}")

        if "Standard Deviation" in indicators:
            std_dev, levels = calculate_standard_deviation(df)
            for level, value in levels.items():
                fig.add_trace(go.Scatter(x=df.index, y=value, mode="lines", name=f"Std Dev {level}", line=dict(dash="dot")))
            st.sidebar.write(f"Écart type : {std_dev:.5f}")

        # Ajout d'options interactives
        fig.update_layout(title=f"{selected_stock} - {timeframe}",
                          xaxis_title="Date",
                          yaxis_title="Prix",
                          xaxis_rangeslider_visible=False)

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Impossible de récupérer les données de l'action sélectionnée.")
