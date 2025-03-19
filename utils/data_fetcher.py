import yfinance as yf
import pandas as pd

def fetch_stock_data(stock_symbol, interval="1d"):
    """Récupère tout l'historique disponible et filtre les 10 dernières années."""
    stock = yf.Ticker(stock_symbol)
    df = stock.history(period="max", interval=interval)

    # Vérifier si les données existent
    if not df.empty:
        df.index = df.index.tz_localize(None)  # Supprime le fuseau horaire
        df = df[df.index >= (pd.Timestamp.now() - pd.DateOffset(years=10))]  # Filtrage 10 ans

    return df

def get_stock_suggestions(query):
    """Renvoie une liste d'actions ou indices correspondant à la recherche."""

    # Essayer de récupérer directement l'actif via Yahoo Finance
    try:
        search_results = yf.Ticker(query)
        if search_results.history(period="1d").empty is False:
            return [query.upper()]  # Si valide, renvoie directement
    except:
        pass  # Ignore les erreurs si l'actif n'est pas trouvé

    # Si pas trouvé, utiliser la liste du S&P 500
    try:
        tickers = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]["Symbol"].tolist()
        return [t for t in tickers if query.upper() in t.upper()][:10]
    except:
        return []  # Si problème, retourne une liste vide