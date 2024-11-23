import pandas as pd

class BacktestEngine:
    def __init__(self, strategy, initial_balance=10000):
        self.strategy = strategy
        self.initial_balance = initial_balance
        self.balance = self.initial_balance
        self.positions = []
        self.trades = []

    def run_backtest(self, data):
        signals = self.strategy.generate_signals(data)
        for i, row in signals.iterrows():
            if row['positions'] == 1:  # Buy signal
                self.open_position(row['Close'])
            elif row['positions'] == -1:  # Sell signal
                self.close_position(row['Close'])
        return self.calculate_performance()

    def open_position(self, price):
        self.positions.append(price)
        print(f"Opened position at {price}")

    def close_position(self, price):
        if self.positions:
            entry_price = self.positions.pop(0)
            profit = (price - entry_price) / entry_price * self.balance
            self.balance += profit
            self.trades.append(profit)
            print(f"Closed position at {price}, Profit: {profit}")

    def calculate_performance(self):
        total_trades = len(self.trades)
        if total_trades == 0:
            return {"Total Profit": 0, "Total Trades": 0, "Success Rate": 0}

        total_profit = sum(self.trades)
        success_rate = sum(1 for trade in self.trades if trade > 0) / total_trades
        return {
            "Initial Balance": self.initial_balance,
            "Final Balance": self.balance,
            "Total Profit": total_profit,
            "Total Trades": total_trades,
            "Success Rate": success_rate * 100
        }

# Example usage
if __name__ == "__main__":
    df = pd.read_csv('historical_data.csv')  # Your historical price data
    strategy = MovingAverageStrategy(short_window=50, long_window=200)
    backtest = BacktestEngine(strategy)
    results = backtest.run_backtest(df)
    print(results)
