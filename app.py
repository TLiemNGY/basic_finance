import os
import json
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.data_fetcher import fetch_stock_data, get_stock_suggestions, fetch_index_regression
from utils.indicators import calculate_linear_regression, calculate_standard_deviation, calculate_sma, calculate_rsi

# Configuration de la page Streamlit
st.set_page_config(page_title="Finance Dashboard", layout="wide")

FAV_PATH = "favorites.json"


def load_favorites():
    if os.path.exists(FAV_PATH):
        with open(FAV_PATH, "r") as f:
            return json.load(f)
    return []


def save_favorites(favs):
    with open(FAV_PATH, "w") as f:
        json.dump(favs, f, indent=2)


# Sidebar : Sélection de l'actif avec recherche améliorée
st.sidebar.title("Sélection de l'actif")
query = st.sidebar.text_input("Tapez le nom ou le ticker d'une action ou crypto")
favorites = load_favorites()
stock_list = get_stock_suggestions(query) if query else []

selected_stock = None

if stock_list:
    selected_stock = st.sidebar.selectbox("Résultats de recherche", stock_list)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Ou choisissez un favori")
elif favorites:
    selected_stock = st.sidebar.selectbox("Mes favoris", favorites)
else:
    st.sidebar.info("Aucun actif sélectionné.")

st.sidebar.markdown("---")

# Indicateurs sélectionnables
indicators = st.sidebar.multiselect("Indicateurs", ["Linear Regression", "Standard Deviation", "SMA", "RSI"])

st.sidebar.markdown("---")
if selected_stock:
    st.sidebar.markdown("### ⭐ Gestion des favoris")
    if selected_stock in favorites:
        if st.sidebar.button("❌ Retirer des favoris"):
            favorites.remove(selected_stock)
            save_favorites(favorites)
            st.rerun()
    else:
        if st.sidebar.button("✅ Ajouter aux favoris"):
            favorites.append(selected_stock)
            save_favorites(favorites)
            st.rerun()

    is_crypto = "-USD" in selected_stock
    is_european = selected_stock.endswith(".PA")
    is_us = not is_crypto and not is_european

    df = fetch_stock_data(selected_stock, "1wk")
    st.sidebar.markdown("---")
    if not df.empty:
        max_lookback = min(780, len(df))
        lookback = st.sidebar.slider("Période de régression (semaines)", 50, max_lookback, max_lookback, 50)
        exclude_weeks = st.sidebar.slider("Exclure les X dernières semaines", 0, lookback, 0)
        lookback_start = exclude_weeks
        lookback_end = lookback

        # Déterminer l’indice de référence
        index_symbol = "BTC-USD" if is_crypto else ("^FCHI" if is_european else "^GSPC")
        index_data = fetch_index_regression(index_symbol) if "Market Linear Regression" in indicators else None

        if index_data is not None and isinstance(index_data, pd.Series):
            index_data = pd.DataFrame({"Close": index_data})

        # Création du graphique avec RSI en sous-graph
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.8, 0.2])

        # Ajout des prix en chandelier
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="Prix"
        ), row=1, col=1)

        regression_line, slope = None, None
        market_regression, market_slope = None, None

        if "Linear Regression" in indicators:
            df_regression = df.iloc[-lookback_end:-lookback_start] if lookback_start != 0 else df.iloc[-lookback_end:]
            regression_line, slope = calculate_linear_regression(df_regression, len(df_regression))

            fig.add_trace(go.Scatter(
                x=df_regression.index,
                y=regression_line,
                mode="lines",
                name="Régression de l'actif",
                line=dict(dash="dash", color="darkblue")
            ), row=1, col=1)

        if "Standard Deviation" in indicators and regression_line is not None:
            std_dev, levels = calculate_standard_deviation(df_regression, regression_line, len(df_regression))
            if std_dev > 0:
                colors = ["orange", "orange", "purple", "purple", "lightblue", "lightblue"]
                for i, (level, value) in enumerate(levels.items()):
                    fig.add_trace(go.Scatter(
                        x=df_regression.index,
                        y=value,
                        mode="lines",
                        name=f"Std Dev {level}",
                        line=dict(dash="dot", color=colors[i % len(colors)], width=1)
                    ), row=1, col=1)

        if "SMA" in indicators:
            sma_50, sma_200 = calculate_sma(df)
            fig.add_trace(go.Scatter(
                x=df.index,
                y=sma_50,
                mode="lines",
                name="SMA 50",
                line=dict(color="blue")
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=df.index,
                y=sma_200,
                mode="lines",
                name="SMA 200",
                line=dict(color="green")
            ), row=1, col=1)

        if "RSI" in indicators:
            rsi = calculate_rsi(df)
            fig.add_trace(go.Scatter(
                x=df.index,
                y=rsi,
                mode="lines",
                name="RSI",
                line=dict(color="purple")
            ), row=2, col=1)

        fig.update_layout(
            title=f"{selected_stock}",
            xaxis=dict(
                title="Date",
                tickformat="%Y-%m-%d",
                tickmode="auto",
                rangeslider_visible=False,
                showticklabels=True
            ),
            xaxis2=dict(showticklabels=False),
            yaxis_title="Prix",
            height=800
        )

        st.plotly_chart(fig, use_container_width=True)

        st.sidebar.markdown("---")

        if regression_line is not None:
            start_price = regression_line[0]
            end_price = regression_line[-1]
            years = lookback / 52
            cagr_asset = (end_price / start_price) ** (1 / years) - 1 if start_price > 0 else 0
            st.sidebar.write(f"**📈 Croissance annualisée de l’actif** : {cagr_asset * 100:.2f}%")

            # Comparaison avec le marché
            index_symbol = "BTC-USD" if is_crypto else ("^FCHI" if is_european else "^GSPC")
            index_data = fetch_index_regression(index_symbol)

            if index_data is not None:
                index_regression = index_data.loc[df_regression.index.min():df_regression.index.max()]
                if not index_regression.empty and len(index_regression) == len(df_regression):
                    market_start = index_regression.iloc[0]
                    market_end = index_regression.iloc[-1]
                    cagr_market = (market_end / market_start) ** (1 / years) - 1 if market_start > 0 else 0
                    st.sidebar.write(
                        f"**📉 Croissance annualisée du marché ({index_symbol})** : {cagr_market * 100:.2f}%")
                    if cagr_asset > cagr_market:
                        st.sidebar.markdown(
                            f"Si l’actif avait suivi la dynamique du {index_symbol}, sa croissance aurait été de **+{cagr_market * 100:.2f}%/an** au lieu de **+{cagr_asset * 100:.2f}%/an**.")
                    elif cagr_asset < cagr_market:
                        st.sidebar.markdown(
                            f"Si l’actif avait suivi la dynamique du {index_symbol}, sa croissance aurait été de **+{cagr_market * 100:.2f}%/an** au lieu de **+{cagr_asset * 100:.2f}%/an**.")
                    else:
                        st.sidebar.markdown(f"L’actif a exactement suivi la même croissance que le {index_symbol}.")

st.sidebar.markdown("---")

# Explication sur les SMA
st.sidebar.markdown("### **Comment lire les SMA ?**")
st.sidebar.markdown(
    "- **SMA 50** (bleu) : Tendance **moyen terme**.\n"
    "- **SMA 200** (vert) : Tendance **long terme**.\n"
    "- **Si SMA 50 passe au-dessus de SMA 200** → **Signal haussier**.\n"
    "- **Si SMA 50 passe sous SMA 200** → **Signal baissier**."
)