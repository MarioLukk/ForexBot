import sqlite3

def save_signal(pair, signal, rsi):
    conn = sqlite3.connect('forex.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pair TEXT,
                    signal TEXT,
                    rsi REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')
    c.execute('INSERT INTO signals (pair, signal, rsi) VALUES (?, ?, ?)', (pair, signal, rsi))
    conn.commit()
    conn.close()
