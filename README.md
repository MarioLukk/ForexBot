# 📈 ForexBot – Aplicație de analiză Forex cu indicatori tehnici

**ForexBot** este o aplicație web locală care preia și afișează date din piața Forex folosind API-ul Alpha Vantage. Oferă vizualizări grafice de tip candlestick și interpretarea automată a celor mai folosiți indicatori tehnici:

- **RSI** – Relative Strength Index  
- **SMA** – Simple Moving Average  
- **EMA** – Exponential Moving Average  
- **MACD** – Moving Average Convergence Divergence  
- **Bollinger Bands**

---

## 🔧 Tehnologii folosite

- **Backend:** Python (`Flask`), `SQLite`
- **Frontend:** HTML, `TailwindCSS`, `Plotly.js`
- **API de date:** [Alpha Vantage](https://www.alphavantage.co/)

---

## 📦 Instalare & rulare

1. Clonează proiectul:
   git clone https://github.com/username/forexbot.git
   cd forexbot
   
2. Creează un mediu virtual (opțional):
python -m venv .venv
source .venv/bin/activate
sau
.venv\Scripts\activate pe Windows

3. Instalează dependințele:

pip install -r requirements.txt

4. Rulează aplicația backend:

python backend/app.py

Aplicația va porni la adresa: http://127.0.0.1:5000

Deschide manual fișierul frontend/index.html în browser pentru interfața grafică.

⚙️ Configurații
Cheia API Alpha Vantage este setată în fișierul app.py, în variabila API_KEY.

Datele sunt stocate local în fișierul forex.db (SQLite).

Caching-ul este implementat pentru a limita apelurile către API și pentru o performanță mai bună.

🧠 Funcționalități
Selectare pereche valutară (ex: EURUSD)

Alegere interval temporal: zilnic, săptămânal, lunar

Configurare parametri pentru fiecare indicator tehnic

Grafic interactiv candlestick + suprapunere indicatori

Istoric cu ultimele 50 de analize

Suport pentru mod Light/Dark

📋 TODO – Funcționalități în dezvoltare
Afișare automată semnale de tip BUY / SELL pe baza indicatorilor

Strategie combinată cu scor pe indicatori multipli

Export analize în format .CSV

Autentificare utilizator (opțional)
