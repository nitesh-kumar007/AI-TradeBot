# import time
# import random
# import requests
# import threading
# from flask import Flask, render_template
# from flask_socketio import SocketIO

# app = Flask(__name__)
# socketio = SocketIO(app)

# bot_running = False
# trade_history = []
# available_balance = 1000

# # Initialize the last price with a realistic value
# last_price = 50000.0  # Default for Bitcoin

# # Function to fetch live price with retry logic
# def fetch_live_price(pair):
#     try:
#         url = f"https://api.coingecko.com/api/v3/simple/price?ids={pair}&vs_currencies=usd"
#         response = requests.get(url, headers={"Cache-Control": "no-cache"})
#         response.raise_for_status()
#         data = response.json()
#         price = data.get(pair, {}).get("usd", 0)
#         print(f"Fetched price for {pair}: {price}")
#         return price
#     except requests.exceptions.RequestException as e:
#         print(f"API Error: {e}")
#         return None

# # Simulate dynamic price updates
# def simulate_price(pair):
#     global last_price
#     while True:
#         try:
#             # Attempt to fetch live price
#             live_price = fetch_live_price(pair)
#             if live_price is not None and live_price > 0:
#                 last_price = live_price
#             else:
#                 # Simulate fluctuations if live price fails
#                 fluctuation = random.uniform(-0.5, 0.5)  # Up/down by 0.5%
#                 last_price *= 1 + (fluctuation / 100)

#             current_time = time.strftime("%H:%M:%S")
#             socketio.emit("price_update", {"price": round(last_price, 2), "time": current_time})
#             print(f"Updated price: {round(last_price, 2)} at {current_time}")
#         except Exception as e:
#             print(f"Error in simulate_price: {e}")
#         time.sleep(3)  # Update every 3 seconds

# # Trading bot logic
# def trading_bot(trade_amount, pair, single_trade=False):
#     global available_balance, bot_running
#     while bot_running:
#         entry_price = fetch_live_price(pair)
#         if entry_price is None or entry_price <= 0:
#             print("Invalid entry price. Skipping trade.")
#             time.sleep(5)
#             continue

#         qty = trade_amount / entry_price
#         sold_price = entry_price * 1.02  # Simulate 2% profit
#         profit_loss = (sold_price - entry_price) * qty
#         available_balance += profit_loss

#         trade_history.append(
#             {"purchasedPrice": entry_price, "soldPrice": sold_price, "profitLoss": profit_loss}
#         )

#         socketio.emit(
#             "trade_update",
#             {"purchasedPrice": entry_price, "soldPrice": sold_price, "profitLoss": profit_loss},
#         )

#         if single_trade:
#             bot_running = False
#             break

#         time.sleep(5)

# @app.route("/")
# def index():
#     return render_template("index.html")

# @socketio.on("start_bot")
# def start_bot(data):
#     global bot_running, available_balance
#     bot_running = True
#     trade_amount = data.get("amount", 100)
#     currency_pair = data.get("currency", "bitcoin")

#     threading.Thread(
#         target=trading_bot, args=(trade_amount, currency_pair, data.get("single_trade", False))
#     ).start()

# @socketio.on("stop_bot")
# def stop_bot():
#     global bot_running
#     bot_running = False
#     final_profit_loss = sum(trade["profitLoss"] for trade in trade_history)
#     socketio.emit("bot_stopped", final_profit_loss)

# if __name__ == "__main__":
#     threading.Thread(target=simulate_price, args=("bitcoin",)).start()
#     socketio.run(app, debug=True)

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
current_currency = "bitcoin"  # Default currency is Bitcoin

# Fetch live cryptocurrency price
def fetch_live_price(pair):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={pair}&vs_currencies=usd"
        response = requests.get(url)
        response.raise_for_status()  # Ensure we handle bad responses
        data = response.json()
        return data.get(pair, {}).get("usd", 0)
    except Exception as e:
        print(f"Error fetching price for {pair}: {e}")
        return 0

# Simulate Price Updates
def simulate_price():
    global current_currency
    while True:
        if bot_running:
            price = fetch_live_price(current_currency)
            if price > 0:  # Only send data if price is valid
                timestamp = time.strftime("%H:%M:%S")
                socketio.emit("price_update", {"time": timestamp, "price": price})
            else:
                print("Received invalid price. Retrying...")
        time.sleep(2)  # Fetch and emit data every 2 seconds

# Trading Bot Function
def trading_bot(amount, currency_pair):
    global available_balance, trade_history
    entry_price = fetch_live_price(currency_pair)
    time.sleep(1)

    while bot_running:
        exit_price = fetch_live_price(currency_pair)
        profit_loss = exit_price - entry_price
        trade_history.append({
            "purchasedPrice": entry_price,
            "soldPrice": exit_price,
            "profitLoss": profit_loss,
        })
        available_balance += profit_loss

        socketio.emit("trade_update", {
            "purchasedPrice": entry_price,
            "soldPrice": exit_price,
            "profitLoss": profit_loss,
        })
        time.sleep(2)  # Continue trading every 2 seconds

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on("start_bot")
def start_bot(data):
    global bot_running, trade_history
    trade_history = []
    bot_running = True
    socketio.emit("bot_status", {"status": "active"})
    threading.Thread(target=trading_bot, args=(data["amount"], current_currency)).start()

@socketio.on("stop_bot")
def stop_bot():
    global bot_running
    bot_running = False
    socketio.emit("bot_stopped", "Bot has been stopped.")
    socketio.emit("trade_update", {"finalProfitLoss": available_balance})

@socketio.on("change_currency")
def change_currency(data):
    global current_currency
    current_currency = data["currency"]
    print(f"Currency changed to: {current_currency}")
    socketio.emit("currency_changed", {"currency": current_currency})

if __name__ == "__main__":
    threading.Thread(target=simulate_price).start()  # Start the price update thread
    socketio.run(app, host="0.0.0.0", port=5000)
