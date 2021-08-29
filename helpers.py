import pandas as pd 
import talib 
from datetime import datetime, timedelta
import requests 
import time

"""
This contains all helper functions for the backtesting
"""

TICKER_MAPPING = {
    "eth": "ethereum",
    "eos": "eos",
    # USD here maps to tether for coincap
    "usd": "tether",
    "doge": "dogecoin",
    "sol1": "solana",
    "ada": "cardano",
    "xrp": "ripple",
    "dot1": "polkadot",
    "uni3": "uniswap",
    "bch": "bitcoin-cash",
    "ltc": "litecoin",
    "neo": "neo",
    "link": "chainlink",
    "matic": "matic-network",
    "theta": "theta",
    "xlm": "stellar",
    "vet": "vechain",
    "aave": "aave",
    "etc": "ethereum-classic",
    "fil": "filecoin",
    "xmr": "monero",
    "trx": "tron",
    "bnb": "binance-coin",
    "btc": "bitcoin",
    "dot": "polkadot"
}

def EMA_Backtesting(values, n):
    """
    Return exponential moving average of `values`, at
    each step taking into account `n` previous values.
    """
    close = pd.Series(values)
    return talib.EMA(close, timeperiod=n)

def data_fetch_and_format(base, start_time, end_time, index):
    now = datetime.now()
    
    
    # baseId = TICKER_MAPPING[base]
    # baseId = 'xrp'
    quoteId = "tether"
    url = (
        "https://api.coincap.io/v2/candles?exchange=binance&interval=d1"
        f"&baseId={base}&quoteId={quoteId}"
        f"&start={datetime.timestamp(start_time) * 1000}"
        f"&end={datetime.timestamp(end_time) * 1000}"
    )

    response = requests.get(url)
    print(response)
    if response.status_code > 300:
        raise Exception("Invalid response code returned: " + str(response.status_code))
    res = response.json()
    if not res["data"]:
        raise Exception("No response body returned for: " + base)

    data = pd.DataFrame.from_dict(res["data"])
    
    data['period'] = pd.to_datetime(data['period'],unit='ms')

    data = data.set_index(data["period"])
    
    data.index.name = None

    data = data.drop("period", axis = 1)

    data.columns = [title.capitalize() for title in data.columns]

    for name in data.columns:
        data[name] = data[name].astype(float)
    
    data.to_csv(f"{base}.csv", mode = 'a', header = index)







# asset = "link"
# time.sleep(60)
# start_time = datetime(2017, 1, 1, 0, 0) 
# end_time = start_time + timedelta(days = 700)
# data_fetch_and_format(asset, start_time, end_time, True)
# print("Finished 1")

# time.sleep(31)
# start_time = datetime(2018, 12, 2, 0, 0) 
# end_time = start_time + timedelta(days = 700)
# data_fetch_and_format(asset, start_time, end_time, False)
# print("Finished 2")

# time.sleep(31)
# start_time = datetime(2020, 11, 1, 0, 0) 
# end_time = start_time + timedelta(days = 700)
# data_fetch_and_format(asset, start_time, end_time, False)
# print("Finished 3")
