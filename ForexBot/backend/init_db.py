import sqlite3

conn = sqlite3.connect("forex.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pair TEXT NOT NULL,
    interval TEXT NOT NULL,
    period INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    close REAL
)
""")

conn.commit()
conn.close()
print("Tabela 'analyses' a fost creată.")
