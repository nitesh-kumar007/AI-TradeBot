import pandas as pd
import requests
import concurrent.futures
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataFetcher:
    def __init__(self, symbols, interval):
        self.symbols = symbols
        self.interval = interval
        self.base_url = 'https://api.binance.com/api/v3/klines'

    def fetch_symbol_data(self, symbol):
        logger.info(f"Fetching data for {symbol}")
        url = f"{self.base_url}?symbol={symbol}&interval={self.interval}"
        data = requests.get(url).json()
        df = pd.DataFrame(data, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'Ignore'])
        return df

    def fetch_all_data(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.fetch_symbol_data, symbol) for symbol in self.symbols]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        return results
