import requests
import pandas as pd
from config import API_KEY


def get_alpha_data(pair, interval='daily'):
    function_map = {
        'daily': 'FX_DAILY',
        'weekly': 'FX_WEEKLY',
        'monthly': 'FX_MONTHLY'
    }

    function = function_map.get(interval.lower(), 'FX_DAILY')

    params = {
        "function": function,
        "from_symbol": pair[:3],
        "to_symbol": pair[3:],
        "apikey": API_KEY,
        "outputsize": "full" if interval == 'daily' else 'compact'
    }

    r = requests.get("https://www.alphavantage.co/query", params=params)
    data = r.json()

    key_map = {
        'daily': "Time Series FX (Daily)",
        'weekly': "Time Series FX (Weekly)",
        'monthly': "Time Series FX (Monthly)"
    }

    if key_map[interval] not in data:
        return pd.DataFrame()

    df = pd.DataFrame.from_dict(data[key_map[interval]], orient="index", dtype='float')
    df = df.rename(columns={
        "1. open": "open",
        "2. high": "high",
        "3. low": "low",
        "4. close": "close"
    })
    df = df.sort_index()
    df.index = pd.to_datetime(df.index)
    return df


