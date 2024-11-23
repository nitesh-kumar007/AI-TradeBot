import asyncio
from binance.client import Client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradeExecutor:
    def __init__(self, api_key, api_secret):
        self.client = Client(api_key, api_secret)

    async def execute_trade(self, symbol, side, quantity):
        retry_count = 0
        while retry_count < 3:
            try:
                order = self.client.create_order(symbol=symbol, side=side, type='MARKET', quantity=quantity)
                logger.info(f"Trade executed: {order}")
                return order
            except Exception as e:
                logger.error(f"Error executing trade: {e}")
                retry_count += 1
                await asyncio.sleep(2 ** retry_count)
        raise Exception("Failed to execute trade after 3 retries")
