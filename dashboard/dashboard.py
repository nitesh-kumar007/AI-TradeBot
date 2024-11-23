import time
import requests
import threading
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

bot_running = False
trade_history = []
available_balance = 1000

# Fetch live cryptocurrency price
def fetch_live_price(pair):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={pair}&vs_currencies=usd"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get(pair, {}).get("usd", 0)
    except Exception as e:
        print(f"Error fetching price for {pair}: {e}")
        return None  # Return None on error

# Simulate Price Updates
def simulate_price(pair):
    while True:
        price = fetch_live_price(pair)
        if price is not None:  # Only emit data if price is valid
            current_time = time.strftime("%H:%M:%S")
            socketio.emit("price_update", {"price": price, "time": current_time})
        time.sleep(1)

# Trading Bot Logic
def trading_bot(trade_amount, pair, single_trade=False):
    global available_balance, bot_running
    while bot_running:
        entry_price = fetch_live_price(pair)
        if entry_price is None:
            continue
        qty = float(trade_amount) / entry_price

        # Predict price movement (example logic)
        sold_price = entry_price * 1.02  # Simulate 2% rise
        profit_loss = (sold_price - entry_price) * qty

        available_balance += profit_loss
        trade_history.append(
            {"purchasedPrice": entry_price, "soldPrice": sold_price, "profitLoss": profit_loss}
        )
        socketio.emit("trade_update", trade_history[-1])
        if single_trade:
            break

        time.sleep(3)

# Backend Routes
@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("start_bot")
def start_bot(data):
    global bot_running
    bot_running = True

    pair = "bitcoin"  # Change as per user or program interface logic
    trade_amount = data.get("amount")
    threading.Thread(target=trading_bot, args=(trade_amount,)).start()

if __name__ == "__main__":
    # Start the price simulation thread
    threading.Thread(target=simulate_price, args=("bitcoin",)).start()  # Replace with user-selected currency pair
    socketio.run(app, host="0.0.0.0", port=5000)
