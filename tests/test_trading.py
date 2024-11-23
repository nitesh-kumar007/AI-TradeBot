import unittest
import pandas as pd
from app.trading_strategy import MovingAverageStrategy, RSIStrategy

class TestTradingStrategies(unittest.TestCase):
    def setUp(self):
        # Simulated historical data for testing
        data = {'Close': [100, 102, 104, 106, 108, 110, 112, 114, 116, 118]}
        self.df = pd.DataFrame(data)
    
    def test_moving_average_strategy(self):
        strategy = MovingAverageStrategy(short_window=2, long_window=3)
        signals = strategy.generate_signals(self.df)
        self.assertIn('positions', signals)
        self.assertEqual(len(signals['positions']), len(self.df))

    def test_rsi_strategy(self):
        strategy = RSIStrategy(window=3)
        signals = strategy.generate_signals(self.df)
        self.assertIn('signal', signals)
        self.assertEqual(len(signals['signal']), len(self.df))

if __name__ == '__main__':
    unittest.main()
