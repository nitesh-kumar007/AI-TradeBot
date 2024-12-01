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
import random
import requests
import threading
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

bot_running = False
trade_history = []
available_balance = 1000
last_price = 50000.0  # Default price
current_currency = "bitcoin"  # Default currency


def fetch_live_price(pair):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={pair}&vs_currencies=usd"
        response = requests.get(url, headers={"Cache-Control": "no-cache"})
        response.raise_for_status()
        return response.json().get(pair, {}).get("usd", 0)
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return None


def simulate_price():
    global last_price, current_currency
    while True:
        live_price = fetch_live_price(current_currency)
        if live_price:
            last_price = live_price
        else:
            fluctuation = random.uniform(-0.5, 0.5)
            last_price *= 1 + (fluctuation / 100)

        current_time = time.strftime("%H:%M:%S")
        socketio.emit("price_update", {"price": round(last_price, 2), "time": current_time})
        time.sleep(3)


def trading_bot(trade_amount, pair):
    global bot_running, available_balance
    start_time = time.time()
    while bot_running:
        if time.time() - start_time >= 60:  # Stop after 1 minute
            bot_running = False
            break

        entry_price = fetch_live_price(pair)
        if not entry_price:
            time.sleep(5)
            continue

        qty = trade_amount / entry_price
        sold_price = entry_price * 1.02
        profit_loss = (sold_price - entry_price) * qty
        available_balance += profit_loss

        trade_history.append({"purchasedPrice": entry_price, "soldPrice": sold_price, "profitLoss": profit_loss})
        socketio.emit("trade_update", {"purchasedPrice": entry_price, "soldPrice": sold_price, "profitLoss": profit_loss})
        time.sleep(5)


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("change_currency")
def change_currency(data):
    global current_currency
    pair = data.get("currency", "bitcoin")
    current_currency = pair  # Update the global variable
    print(f"Currency changed to: {current_currency}")


@socketio.on("start_bot")
def start_bot(data):
    global bot_running
    bot_running = True
    trade_amount = data.get("amount", 100)
    currency_pair = data.get("currency", "bitcoin")
    threading.Thread(target=trading_bot, args=(trade_amount, currency_pair)).start()


@socketio.on("stop_bot")
def stop_bot():
    global bot_running
    bot_running = False


if __name__ == "__main__":
    threading.Thread(target=simulate_price).start()
    socketio.run(app, debug=True)