from abc import ABC, abstractmethod
import pandas as pd

class TradingStrategy(ABC):
    @abstractmethod
    def generate_signals(self, data):
        pass

class MovingAverageStrategy(TradingStrategy):
    def __init__(self, short_window, long_window):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data):
        data['short_mavg'] = data['Close'].rolling(window=self.short_window, min_periods=1).mean()
        data['long_mavg'] = data['Close'].rolling(window=self.long_window, min_periods=1).mean()
        data['signal'] = 0
        data['signal'][self.short_window:] = np.where(data['short_mavg'][self.short_window:] > data['long_mavg'][self.short_window:], 1, 0)
        data['positions'] = data['signal'].diff()
        return data

class RSIStrategy(TradingStrategy):
    def __init__(self, window=14):
        self.window = window

    def generate_signals(self, data):
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.window).mean()
        rs = gain / loss
        data['rsi'] = 100 - (100 / (1 + rs))
        data['signal'] = np.where(data['rsi'] < 30, 1, np.where(data['rsi'] > 70, -1, 0))
        return data

class StrategyFactory:
    @staticmethod
    def get_strategy(strategy_type, **kwargs):
        if strategy_type == 'moving_average':
            return MovingAverageStrategy(kwargs['short_window'], kwargs['long_window'])
        elif strategy_type == 'rsi':
            return RSIStrategy(kwargs['window'])
        else:
            raise ValueError("Unknown strategy type")
