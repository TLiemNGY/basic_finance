# Basic Finance

## Description

Basic Finance est une application permettant de gérer et d’analyser des données financières de manière simple et efficace. Il est possible d'analyser les actions Euronext (avec ticker, ex : SAFRAN = "SAF.PA", américaines (avec ticker, ex : AMAZON = "AMZN" et des cryptomonnaies (avec la paire, ex : BTC = "BTC-USD").

Elle permet de visualiser la droite de régression, la comparer à l'actif de référence du marché relatif (CAC, S&P, BTC), d'afficher les écarts-types. Pour les analyses intermédiaires, le RSI et la SMA 50/200 sont également disponibles.

## Installation
1. Assurez-vous d'avoir Python 3.11 installé sur votre système.
2. Si vous n'avez pas encore d'environnement virtuel pour ce projet, créez-en un avec la commande suivante

Windows :
   ```bash
   py -3.11 -m venv .venv
   ```

Mac :
   ```bash
   python3 -m venv .venv
   ```

3. Activez l'environnement virtuel :
   - Sous macOS/Linux :
     ```bash
     source .venv/bin/activate
     ```
   - Sous Windows :
     ```bash
     source .venv/Scripts/activate
     ```
4. Installez les dépendances requises :
   ```bash
   pip install -r requirements.txt
   ```

## Utilisation de l'outil :

```bash
   streamlit run app.py
```
