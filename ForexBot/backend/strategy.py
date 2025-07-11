def analyze_rsi_signal(rsi_values, lower=30, upper=70):
    """
    Returnează semnale simple pe baza RSI:
    - 'buy' dacă RSI < lower
    - 'sell' dacă RSI > upper
    - 'hold' altfel
    Ultimul RSI calculat este luat în considerare.
    """
    if not rsi_values or rsi_values[-1] is None:
        return "hold"
    last_rsi = rsi_values[-1]
    if last_rsi < lower:
        return "buy"
    elif last_rsi > upper:
        return "sell"
    else:
        return "hold"
