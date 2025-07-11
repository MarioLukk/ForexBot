import numpy as np

def compute_rsi(close_prices, period=14):
    deltas = np.diff(close_prices)
    seed = deltas[:period]
    up = seed[seed > 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = [100 - (100 / (1 + rs))]

    for delta in deltas[period:]:
        gain = max(delta, 0)
        loss = -min(delta, 0)
        up = (up * (period - 1) + gain) / period
        down = (down * (period - 1) + loss) / period
        rs = up / down if down != 0 else 0
        rsi.append(100 - (100 / (1 + rs)))

    return [None] * period + rsi

def compute_sma(prices, window=14):
    sma = []
    for i in range(len(prices)):
        if i + 1 < window:
            sma.append(None)
        else:
            sma.append(np.mean(prices[i + 1 - window:i + 1]))
    return sma

def compute_ema(prices, window=14):
    ema = []
    k = 2 / (window + 1)
    for i in range(len(prices)):
        if i == 0:
            ema.append(prices[0])
        else:
            ema.append(prices[i] * k + ema[i - 1] * (1 - k))
    return ema

def compute_macd(prices):
    ema_12 = compute_ema(prices, 12)
    ema_26 = compute_ema(prices, 26)
    macd = [a - b for a, b in zip(ema_12, ema_26)]
    signal = compute_ema(macd, 9)
    histogram = [m - s if m and s else None for m, s in zip(macd, signal)]
    return macd, signal, histogram

def compute_bollinger_bands(prices, window=20):
    sma = compute_sma(prices, window)
    stddev = []
    for i in range(len(prices)):
        if i + 1 < window:
            stddev.append(None)
        else:
            stddev.append(np.std(prices[i + 1 - window:i + 1]))
    upper = [s + 2 * d if s and d else None for s, d in zip(sma, stddev)]
    lower = [s - 2 * d if s and d else None for s, d in zip(sma, stddev)]
    return upper, lower
