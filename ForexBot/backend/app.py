from flask import Flask, request, jsonify
import requests
import sqlite3
import time
import json
from flask_cors import CORS

from indicators import compute_rsi, compute_sma, compute_ema, compute_macd, compute_bollinger_bands
from strategy import analyze_rsi_signal

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
        signal = analyze_rsi_signal(cached.get("rsi", []))
        cached["signal"] = signal
        return jsonify({"chart": cached})

    chart_data = fetch_forex_data(pair, interval, period, rsi_len, sma_len, ema_len)
    if chart_data:
        save_to_cache(pair, interval, period, chart_data)
        signal = analyze_rsi_signal(chart_data.get("rsi", []))
        chart_data["signal"] = signal
        return jsonify({"chart": chart_data})
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
