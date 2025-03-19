import yfinance as yf
import pandas as pd

def fetch_stock_data(stock_symbol, interval="1d"):
    """Récupère les données historiques d'une action depuis Yahoo Finance."""
    stock = yf.Ticker(stock_symbol)
    df = stock.history(period="1y", interval=interval)
    return df

def get_stock_suggestions(query):
    """Renvoie une liste d'actions correspondant à la recherche."""
    tickers = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]["Symbol"].tolist()
    return [t for t in tickers if query.upper() in t.upper()][:10]
