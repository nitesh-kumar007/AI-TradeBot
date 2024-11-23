class RiskManagement:
    def __init__(self, portfolio_balance):
        self.portfolio_balance = portfolio_balance

    def calculate_position_size(self, risk_percentage, current_price):
        risk_amount = self.portfolio_balance * (risk_percentage / 100)
        position_size = risk_amount / current_price
        return position_size

    def apply_risk_controls(self, stop_loss, take_profit, entry_price):
        stop_loss_price = entry_price * (1 - stop_loss / 100)
        take_profit_price = entry_price * (1 + take_profit / 100)
        return stop_loss_price, take_profit_price
