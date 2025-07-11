# 📈 ForexBot – Aplicație de analiză Forex cu indicatori tehnici

**ForexBot** este o aplicație web care preia și afișează date Forex din sursa Alpha Vantage, oferind vizualizări grafice și indicatori tehnici precum:
- RSI (Relative Strength Index)
- SMA (Simple Moving Average)
- EMA (Exponential Moving Average)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands

## 🔧 Tehnologii folosite
- **Backend:** Python (Flask), SQLite
- **Frontend:** HTML, TailwindCSS, Plotly.js
- **API de date:** [Alpha Vantage](https://www.alphavantage.co/)

---

## 📦 Instalare & rulare

1. **Clonează proiectul:**

```bash
git clone https://github.com/username/forexbot.git
cd forexbot
2. Creează un mediu virtual (opțional):
```bash
python -m venv .venv
source .venv/bin/activate  # sau .venv\Scripts\activate pe Windows

3. Instalează dependințele:
```bash
pip install -r requirements.txt

4. Rulează aplicația:
```bash
python backend/app.py

Aplicația va porni pe http://127.0.0.1:5000

5. Deschide fișierul index.html din folderul frontend în browser.

⚙️ Configurații
Cheia Alpha Vantage este setată în fișierul app.py în variabila API_KEY.

Datele sunt salvate local în forex.db (SQLite).

Caching-ul este implementat pentru reducerea apelurilor la API.

🧠 Funcționalități
Selecție pereche valutară (ex: EURUSD)

Alegere interval: zilnic / săptămânal / lunar

Configurare perioadă analiză + parametri indicatori (RSI, SMA, EMA)

Grafic tip candlestick + suprapunere indicatori

Istoric ultimele 50 de analize

Mod light/dark

📋 TODO (în dezvoltare)
Afișare semnale automate (BUY / SELL)

Strategie pe indicatori multipli

Export istoric în CSV

Autentificare utilizator (opțional)
