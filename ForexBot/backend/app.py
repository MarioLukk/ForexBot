from flask import Flask, request, jsonify
import requests
import sqlite3
import time
import json
from flask_cors import CORS

from indicators import compute_rsi, compute_sma, compute_ema, compute_macd, compute_bollinger_bands

app = Flask(__name__)
CORS(app)
API_KEY = "MPFFQ2KFNCTNYJ5A"

def init_db():
    conn = sqlite3.connect("forex.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            pair TEXT,
            interval TEXT,
            period INTEGER,
            timestamp INTEGER,
            json_data TEXT,
            PRIMARY KEY (pair, interval, period)
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pair TEXT,
            interval TEXT,
            period INTEGER,
            timestamp TEXT,
            close REAL
        );
    """)
    conn.commit()
    conn.close()

def get_cached_data(pair, interval, period, ttl=60):
    conn = sqlite3.connect("forex.db")
    cursor = conn.cursor()
    now = int(time.time())
    cursor.execute("""
        SELECT timestamp, json_data FROM cache 
        WHERE pair=? AND interval=? AND period=?
    """, (pair, interval, period))
    row = cursor.fetchone()
    if row:
        ts, json_str = row
        if now - ts < ttl:
            conn.close()
            return json.loads(json_str)
    conn.close()
    return None

def save_to_cache(pair, interval, period, data):
    conn = sqlite3.connect("forex.db")
    cursor = conn.cursor()
    now = int(time.time())
    json_str = json.dumps(data)
    cursor.execute("""
        INSERT OR REPLACE INTO cache (pair, interval, period, timestamp, json_data)
        VALUES (?, ?, ?, ?, ?)
    """, (pair, interval, period, now, json_str))
    conn.commit()
    conn.close()

def get_rsi_state(rsi_value):
    if rsi_value is None:
        return "Indisponibil"
    if rsi_value > 70:
        return "Supracumpărat"
    elif rsi_value < 30:
        return "Supravândut"
    else:
        return "Neutru"

def fetch_forex_data(pair, interval, period, rsi_len=14, sma_len=14, ema_len=14):
    function_map = {
        "daily": "FX_DAILY",
        "weekly": "FX_WEEKLY",
        "monthly": "FX_MONTHLY"
    }
    function = function_map.get(interval.lower())
    if not function:
        return None

    from_symbol = pair[:3]
    to_symbol = pair[3:]
    url = f"https://www.alphavantage.co/query"
    params = {
        "function": function,
        "from_symbol": from_symbol,
        "to_symbol": to_symbol,
        "apikey": API_KEY,
        "outputsize": "compact"
    }
    response = requests.get(url, params=params)
    data = response.json()
    time_series_key = next((k for k in data if "Time Series" in k), None)
    if not time_series_key or time_series_key not in data:
        return None

    time_series = data[time_series_key]
    sorted_dates = sorted(time_series.keys(), reverse=True)[:period]

    chart_data = {
        "dates": [],
        "open": [],
        "high": [],
        "low": [],
        "close": []
    }
    for date in reversed(sorted_dates):
        day_data = time_series[date]
        chart_data["dates"].append(date)
        chart_data["open"].append(float(day_data["1. open"]))
        chart_data["high"].append(float(day_data["2. high"]))
        chart_data["low"].append(float(day_data["3. low"]))
        chart_data["close"].append(float(day_data["4. close"]))

    closes = chart_data["close"]
    chart_data["rsi"] = compute_rsi(closes, rsi_len)
    chart_data["sma"] = compute_sma(closes, sma_len)
    chart_data["ema"] = compute_ema(closes, ema_len)
    macd, signal, hist = compute_macd(closes)
    chart_data["macd"] = macd
    chart_data["macd_signal"] = signal
    chart_data["macd_hist"] = hist
    macd_alert = analyze_macd_simple(chart_data["macd"], chart_data["macd_signal"])
    chart_data["macd_signal_text"] = macd_alert
    upper, lower = compute_bollinger_bands(closes)
    chart_data["bb_upper"] = upper
    chart_data["bb_lower"] = lower

    if chart_data["dates"]:
        conn = sqlite3.connect("forex.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO history (pair, interval, period, timestamp, close)
            VALUES (?, ?, ?, ?, ?)
        """, (pair, interval, period, chart_data["dates"][-1], chart_data["close"][-1]))
        conn.commit()
        conn.close()

    return chart_data

def analyze_macd_simple(macd, signal):
    if not macd or not signal:
        return "MACD Neutru"
    last_macd = macd[-1]
    last_signal = signal[-1]
    if last_macd > last_signal:
        return "MACD bullish - Semnal de cumpărare"
    elif last_macd < last_signal:
        return "MACD bearish - Semnal de vânzare"
    else:
        return "MACD Neutru"

def analyze_sma_ema_simple(sma, ema):
        if not sma or not ema:
            return "SMA/EMA Neutru"
        last_sma = sma[-1]
        last_ema = ema[-1]
        if last_ema > last_sma:
            return "EMA > SMA - Semnal Bullish"
        elif last_ema < last_sma:
            return "EMA < SMA - Semnal Bearish"
        else:
            return "EMA = SMA - Semnal Neutru"


def analyze_bollinger_signal(close, bb_upper, bb_lower):
    if not close or not bb_upper or not bb_lower:
        return "Bollinger Neutru"

    last_price = close[-1]
    last_upper = bb_upper[-1]
    last_lower = bb_lower[-1]

    if last_price >= last_upper:
        return "Bollinger - Semnal de vânzare"
    elif last_price <= last_lower:
        return "Bollinger - Semnal de cumpărare"
    else:
        return "Bollinger Neutru"

def compute_overall_signal(rsi_state, macd_state, sma_ema_state, bollinger_state):
    score = 0

    # RSI scoring
    if rsi_state == "Supravândut":
        score += 1
    elif rsi_state == "Supracumpărat":
        score -= 1

    # MACD scoring
    if "bullish" in macd_state.lower():
        score += 1
    elif "bearish" in macd_state.lower():
        score -= 1

    # SMA/EMA scoring
    if "bullish" in sma_ema_state.lower():
        score += 1
    elif "bearish" in sma_ema_state.lower():
        score -= 1

    # Bollinger scoring
    if "cumpărare" in bollinger_state.lower():
        score += 1
    elif "vânzare" in bollinger_state.lower():
        score -= 1

    # Interpretare scor
    if score >= 2:
        return "✅ Recomandare: CUMPĂRARE"
    elif score <= -2:
        return "❌ Recomandare: VÂNZARE"
    else:
        return "⚖️ Recomandare: AȘTEPTARE / HOLD"



@app.route("/api/signal")
def get_signal():
    pair = request.args.get("pair")
    interval = request.args.get("interval")
    period = int(request.args.get("period", 30))
    rsi_len = int(request.args.get("rsi", 14))
    sma_len = int(request.args.get("sma", 14))
    ema_len = int(request.args.get("ema", 14))

    if not pair or not interval:
        return jsonify({"error": "Parametri lipsă"}), 400

    cached = get_cached_data(pair, interval, period)
    if cached:
        latest_rsi = cached.get("rsi", [])[-1] if cached.get("rsi") else None
        rsi_state = get_rsi_state(latest_rsi)

        macd_values = cached.get("macd", [])
        macd_signal_values = cached.get("macd_signal", [])
        macd_state = analyze_macd_simple(macd_values, macd_signal_values)

        sma = cached.get("sma", [])
        ema = cached.get("ema", [])
        sma_ema_state = analyze_sma_ema_simple(sma, ema)
        bollinger_state = analyze_bollinger_signal(cached.get("close"), cached.get("bb_upper"),
                                                   cached.get("bb_lower"))
        overall_signal = compute_overall_signal(
            rsi_state, macd_state, sma_ema_state, bollinger_state
        )

        return jsonify({
            "chart": cached,
            "rsi": latest_rsi,
            "rsi_state": rsi_state,
            "macd_state": macd_state,
            "sma_ema_state": sma_ema_state,
            "bollinger_state": bollinger_state,
            "overall_signal": overall_signal
        })

    chart_data = fetch_forex_data(pair, interval, period, rsi_len, sma_len, ema_len)
    if chart_data:
        save_to_cache(pair, interval, period, chart_data)
        latest_rsi = chart_data.get("rsi", [])[-1] if chart_data.get("rsi") else None
        rsi_state = get_rsi_state(latest_rsi)

        macd_values = chart_data.get("macd", [])
        macd_signal_values = chart_data.get("macd_signal", [])
        macd_state = analyze_macd_simple(macd_values, macd_signal_values)

        sma = chart_data.get("sma", [])
        ema = chart_data.get("ema", [])
        sma_ema_state = analyze_sma_ema_simple(sma, ema)
        bollinger_state = analyze_bollinger_signal(chart_data.get("close"), chart_data.get("bb_upper"),
                                                   chart_data.get("bb_lower"))
        overall_signal = compute_overall_signal(
            rsi_state, macd_state, sma_ema_state, bollinger_state
        )

        return jsonify({
            "chart": chart_data,
            "rsi": latest_rsi,
            "rsi_state": rsi_state,
            "macd_state": macd_state,
            "sma_ema_state": sma_ema_state,
            "bollinger_state": bollinger_state,
            "overall_signal": overall_signal
        })
    else:
        return jsonify({"error": "Datele nu au fost returnate corect de Alpha Vantage."}), 500


@app.route("/api/history")
def get_history():
    conn = sqlite3.connect("forex.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT pair, interval, period, timestamp, close 
        FROM history 
        ORDER BY id DESC 
        LIMIT 50
    """)
    rows = cursor.fetchall()
    conn.close()
    result = []
    for row in rows:
        result.append({
            "pair": row[0],
            "interval": row[1],
            "period": row[2],
            "timestamp": row[3],
            "close": row[4]
        })
    return jsonify(result)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
