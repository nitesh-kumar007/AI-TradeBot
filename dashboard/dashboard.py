# # import time
# # import random
# # import requests
# # import threading
# # from flask import Flask, render_template
# # from flask_socketio import SocketIO

# # app = Flask(__name__)
# # socketio = SocketIO(app)

# # # Globals
# # bot_running = False
# # trade_history = []
# # available_balance = 1000.0
# # last_price = 50000.0
# # current_currency = "bitcoin"

# # # Price simulation and threading
# # simulation_thread = None
# # stop_price_simulation = threading.Event()
# # thread_lock = threading.Lock()

# # # Moving average calculation
# # price_data = []
# # short_window = 5
# # long_window = 15

# # # Fetch live price from API
# # def fetch_live_price(pair):
# #     try:
# #         url = f"https://api.coingecko.com/api/v3/simple/price?ids={pair}&vs_currencies=usd"
# #         response = requests.get(url, headers={"Cache-Control": "no-cache"})
# #         response.raise_for_status()
# #         return response.json().get(pair, {}).get("usd", 0)
# #     except requests.exceptions.RequestException as e:
# #         print(f"API Error: {e}")
# #         return None

# # # Simulate price changes
# # def simulate_price():
# #     global last_price, current_currency, price_data
# #     print(f"Started price simulation for {current_currency}")
# #     while not stop_price_simulation.is_set():
# #         live_price = fetch_live_price(current_currency)
# #         if live_price:
# #             last_price = live_price
# #         else:
# #             fluctuation = random.uniform(-0.5, 0.5)
# #             last_price *= 1 + (fluctuation / 100)

# #         price_data.append(last_price)
# #         if len(price_data) > long_window:
# #             price_data.pop(0)

# #         current_time = time.strftime("%H:%M:%S")
# #         socketio.emit("price_update", {
# #             "price": round(last_price, 2),
# #             "time": current_time,
# #             "currency": current_currency
# #         })

# #         if stop_price_simulation.wait(2):
# #             break

# #     print(f"Stopped price simulation for {current_currency}")

# # # Calculate moving average
# # def calculate_moving_average(data, window):
# #     if len(data) < window:
# #         return None
# #     return sum(data[-window:]) / window

# # # Moving average crossover strategy
# # def moving_average_crossover_strategy():
# #     short_ma = calculate_moving_average(price_data, short_window)
# #     long_ma = calculate_moving_average(price_data, long_window)
# #     if short_ma and long_ma:
# #         if short_ma > long_ma:
# #             return "buy"
# #         elif short_ma < long_ma:
# #             return "sell"
# #     return "hold"

# # def trading_bot(trade_amount, pair):
# #     global bot_running, available_balance
# #     bought = False
# #     qty = 0
# #     entry_price = 0

# #     stop_loss = 0.98  # Stop loss at 98% of buy price
# #     take_profit = 1.02  # Take profit at 102% of buy price
# #     last_trade_time = time.time()  # Timestamp of the last trade
# #     start_time = time.time()  # Start time of the bot

# #     print("Trading bot started.")
# #     while bot_running:
# #         # Check if 5 minutes have passed
# #         elapsed_time = time.time() - start_time
# #         if elapsed_time > 300:  # 5 minutes = 300 seconds
# #             print("Trading session timed out.")
# #             socketio.emit("bot_status", {"status": "completed"})
# #             break

# #         # Ensure trades happen every 1 minute
# #         if time.time() - last_trade_time < 60:
# #             time.sleep(1)  # Wait a bit before re-checking
# #             continue

# #         # Fetch the live price
# #         live_price = fetch_live_price(pair)
# #         if not live_price:
# #             continue

# #         # If not holding, consider buying
# #         if not bought and available_balance >= trade_amount:
# #             qty = trade_amount / live_price
# #             entry_price = live_price
# #             available_balance -= trade_amount
# #             bought = True
# #             trade_history.append({"action": "buy", "price": entry_price, "qty": qty})
# #             last_trade_time = time.time()
# #             print(f"Bought {qty:.6f} at ${entry_price:.2f}")

# #             # Emit buy action to the frontend
# #             socketio.emit("trade_update", {
# #                 "action": "buy",
# #                 "price": entry_price,
# #                 "profitLoss": 0,
# #                 "balance": available_balance
# #             })

# #         # If holding, consider selling
# #         elif bought:
# #             if live_price >= entry_price * take_profit or live_price <= entry_price * stop_loss:
# #                 profit_loss = (live_price * qty) - (entry_price * qty)
# #                 available_balance += live_price * qty
# #                 trade_history.append({"action": "sell", "price": live_price, "profitLoss": profit_loss})
# #                 bought = False
# #                 last_trade_time = time.time()
# #                 print(f"Sold {qty:.6f} at ${live_price:.2f}, Profit/Loss: ${profit_loss:.2f}")

# #                 # Emit sell action to the frontend
# #                 socketio.emit("trade_update", {
# #                     "action": "sell",
# #                     "price": live_price,
# #                     "profitLoss": profit_loss,
# #                     "balance": available_balance
# #                 })

# #     # Emit summary when the bot stops
# #     total_profit_loss = sum(
# #         trade.get("profitLoss", 0) for trade in trade_history if trade["action"] == "sell"
# #     )
# #     socketio.emit("trade_summary", {"total_profit_loss": total_profit_loss})
# #     print("Trading bot stopped.")

# # # Restart price simulation
# # def restart_price_simulation():
# #     global simulation_thread
# #     with thread_lock:
# #         stop_price_simulation.set()
# #         if simulation_thread and simulation_thread.is_alive():
# #             simulation_thread.join()

# #         stop_price_simulation.clear()
# #         simulation_thread = threading.Thread(target=simulate_price, daemon=True)
# #         simulation_thread.start()

# # @app.route("/")
# # def index():
# #     return render_template("index.html")

# # @socketio.on("change_currency")
# # def change_currency(data):
# #     global current_currency
# #     pair = data.get("currency", "bitcoin")
# #     if pair != current_currency:
# #         current_currency = pair
# #         print(f"Currency changed to: {current_currency}")
# #         restart_price_simulation()
# #         socketio.emit("clear_chart")

# # @socketio.on("start_bot")
# # def start_bot(data):
# #     global bot_running
# #     bot_running = True
# #     trade_amount = float(data.get("amount", 100))
# #     currency_pair = data.get("currency", current_currency)
# #     socketio.emit("bot_status", {"status": "active"})
# #     threading.Thread(target=trading_bot, args=(trade_amount, currency_pair), daemon=True).start()

# # @socketio.on("stop_bot")
# # def stop_bot():
# #     global bot_running
# #     bot_running = False
# #     total_profit_loss = sum(
# #         trade.get("profitLoss", 0) for trade in trade_history if trade["action"] == "sell"
# #     )
# #     socketio.emit("bot_status", {"status": "inactive"})
# #     socketio.emit("trade_summary", {"total_profit_loss": total_profit_loss})

# # if __name__ == "__main__":
# #     restart_price_simulation()
# #     socketio.run(app, debug=True)


# import time
# import random
# import requests
# import threading
# from flask import Flask, render_template
# from flask_socketio import SocketIO

# app = Flask(__name__)
# socketio = SocketIO(app)

# # Globals
# bot_running = False
# trade_history = []
# available_balance = 1000.0
# last_price = 50000.0  # Default price
# current_currency = "bitcoin"  # Default currency
# simulation_thread = None
# stop_price_simulation = threading.Event()  # Event to signal stopping
# thread_lock = threading.Lock()  # Lock for thread safety

# price_data = []  # Store price data for moving average calculation
# short_window = 5  # Short-term moving average window
# long_window = 15  # Long-term moving average window

# # Fetch live price from API
# def fetch_live_price(pair):
#     try:
#         url = f"https://api.coingecko.com/api/v3/simple/price?ids={pair}&vs_currencies=usd"
#         response = requests.get(url, headers={"Cache-Control": "no-cache"})
#         response.raise_for_status()
#         return response.json().get(pair, {}).get("usd", 0)
#     except requests.exceptions.RequestException as e:
#         print(f"API Error: {e}")
#         return None

# # Simulate price changes
# def simulate_price():
#     global last_price, current_currency, price_data

#     print(f"Started price simulation for {current_currency}")
#     while not stop_price_simulation.is_set():
#         live_price = fetch_live_price(current_currency)
#         if live_price:
#             last_price = live_price
#         else:
#             fluctuation = random.uniform(-0.5, 0.5)
#             last_price *= 1 + (fluctuation / 100)

#         # Append price to the data list
#         price_data.append(last_price)
#         if len(price_data) > long_window:
#             price_data.pop(0)  # Keep only the required window size

#         current_time = time.strftime("%H:%M:%S")
#         socketio.emit("price_update", {
#             "price": round(last_price, 2),
#             "time": current_time,
#             "currency": current_currency
#         })

#         if stop_price_simulation.wait(2):
#             break

#     print(f"Stopped price simulation for {current_currency}")

# # Calculate moving average
# def calculate_moving_average(data, window):
#     if len(data) < window:
#         return None
#     return sum(data[-window:]) / window

# # Moving average crossover strategy
# def moving_average_crossover_strategy():
#     short_ma = calculate_moving_average(price_data, short_window)
#     long_ma = calculate_moving_average(price_data, long_window)

#     if short_ma and long_ma:
#         if short_ma > long_ma:
#             return "buy"
#         elif short_ma < long_ma:
#             return "sell"
#     return "hold"

# def trading_bot(trade_amount, pair):
#     global bot_running, available_balance
#     bought = False
#     qty = 0
#     entry_price = 0

#     stop_loss = 0.98  # Stop loss at 98% of buy price
#     take_profit = 1.02  # Take profit at 102% of buy price
#     last_trade_time = time.time()  # Timestamp of the last trade
#     start_time = time.time()  # Start time of the bot

#     print("Trading bot started.")
#     while bot_running:
#         # Stop bot after 5 minutes
#         if time.time() - start_time > 300:  # 5 minutes = 300 seconds
#             print("Trading session timed out.")
#             socketio.emit("bot_status", {"status": "completed"})
#             break

#         # Wait for 1-minute interval
#         if time.time() - last_trade_time < 60:
#             time.sleep(1)  # Prevent busy looping
#             continue

#         # Fetch live price
#         live_price = fetch_live_price(pair)
#         if not live_price:
#             continue

#         # If not holding, consider buying
#         if not bought and available_balance >= trade_amount:
#             strategy_signal = moving_average_crossover_strategy()
#             if strategy_signal == "buy":
#                 qty = trade_amount / live_price
#                 entry_price = live_price
#                 available_balance -= trade_amount
#                 bought = True
#                 trade_history.append({"action": "buy", "price": entry_price, "qty": qty})
#                 last_trade_time = time.time()
#                 print(f"Bought {qty:.6f} at ${entry_price:.2f}")

#                 # Emit buy action to frontend
#                 socketio.emit("trade_update", {
#                     "action": "buy",
#                     "price": entry_price,
#                     "profitLoss": 0,
#                     "balance": available_balance
#                 })

#         # If holding, consider selling
#         elif bought:
#             if live_price >= entry_price * take_profit or live_price <= entry_price * stop_loss:
#                 profit_loss = (live_price * qty) - (entry_price * qty)
#                 available_balance += live_price * qty
#                 trade_history.append({"action": "sell", "price": live_price, "profitLoss": profit_loss})
#                 bought = False
#                 last_trade_time = time.time()
#                 print(f"Sold {qty:.6f} at ${live_price:.2f}, Profit/Loss: ${profit_loss:.2f}")

#                 # Emit sell action to frontend
#                 socketio.emit("trade_update", {
#                     "action": "sell",
#                     "price": live_price,
#                     "profitLoss": profit_loss,
#                     "balance": available_balance
#                 })

#     # Emit summary when the bot stops
#     total_profit_loss = sum(
#         trade.get("profitLoss", 0) for trade in trade_history if trade["action"] == "sell"
#     )
#     socketio.emit("trade_summary", {"total_profit_loss": total_profit_loss})
#     print("Trading bot stopped.")



# # Restart price simulation thread
# def restart_price_simulation():
#     global simulation_thread

#     with thread_lock:
#         stop_price_simulation.set()
#         if simulation_thread and simulation_thread.is_alive():
#             simulation_thread.join()

#         stop_price_simulation.clear()
#         simulation_thread = threading.Thread(target=simulate_price, daemon=True)
#         simulation_thread.start()

# @app.route("/")
# def index():
#     return render_template("index.html")

# @socketio.on("change_currency")
# def change_currency(data):
#     global current_currency
#     pair = data.get("currency", "bitcoin")
#     if pair != current_currency:
#         current_currency = pair
#         print(f"Currency changed to: {current_currency}")
#         restart_price_simulation()
#         socketio.emit("clear_chart")

# @socketio.on("start_bot")
# def start_bot(data):
#     global bot_running
#     bot_running = True
#     trade_amount = float(data.get("amount", 100))
#     currency_pair = data.get("currency", current_currency)  # Use provided currency or fallback
#     socketio.emit("bot_status", {"status": "active"})
#     threading.Thread(target=trading_bot, args=(trade_amount, currency_pair), daemon=True).start()

# @socketio.on("stop_bot")
# def stop_bot():
#     global bot_running
#     bot_running = False

#     # Calculate total profit/loss from trade history
#     total_profit_loss = sum(
#         trade.get("profitLoss", 0) for trade in trade_history if trade["action"] == "sell"
#     )
#     socketio.emit("bot_status", {"status": "inactive"})
#     socketio.emit("trade_summary", {"total_profit_loss": total_profit_loss})


# if __name__ == "__main__":
#     restart_price_simulation()
#     socketio.run(app, debug=True)



import time
import random
import requests
import threading
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

# Globals
bot_running = False
trade_history = []
available_balance = 1000.0
last_price = 50000.0  # Default price
current_currency = "bitcoin"  # Default currency
simulation_thread = None
stop_price_simulation = threading.Event()  # Event to signal stopping
thread_lock = threading.Lock()  # Lock for thread safety

price_data = []  # Store price data for moving average calculation
short_window = 5  # Short-term moving average window
long_window = 15  # Long-term moving average window


# Fetch live price from API
def fetch_live_price(pair):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={pair}&vs_currencies=usd"
        response = requests.get(url, headers={"Cache-Control": "no-cache"})
        response.raise_for_status()
        price = response.json().get(pair, {}).get("usd", 0)
        print(f"Fetched live price for {pair}: {price}")
        return price
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return None


# Simulate price changes
def simulate_price():
    global last_price, current_currency, price_data

    print(f"Started price simulation for {current_currency}")
    while not stop_price_simulation.is_set():
        live_price = fetch_live_price(current_currency)
        if live_price:
            last_price = live_price
        else:
            fluctuation = random.uniform(-0.5, 0.5)
            last_price *= 1 + (fluctuation / 100)

        price_data.append(last_price)
        if len(price_data) > long_window:
            price_data.pop(0)

        current_time = time.strftime("%H:%M:%S")
        socketio.emit("price_update", {
            "price": round(last_price, 2),
            "time": current_time,
            "currency": current_currency
        })

        print(f"Price updated: {round(last_price, 2)} at {current_time}")

        if stop_price_simulation.wait(2):
            break

    print(f"Stopped price simulation for {current_currency}")


# Calculate moving average
def calculate_moving_average(data, window):
    if len(data) < window:
        return None
    return sum(data[-window:]) / window


# Moving average crossover strategy
def moving_average_crossover_strategy():
    short_ma = calculate_moving_average(price_data, short_window)
    long_ma = calculate_moving_average(price_data, long_window)
    print(f"Short MA: {short_ma}, Long MA: {long_ma}")

    if short_ma and long_ma:
        if short_ma > long_ma:
            return "buy"
        elif short_ma < long_ma:
            return "sell"
    return "hold"


def trading_bot(trade_amount, pair):
    global bot_running, available_balance
    bought = False
    qty = 0
    entry_price = 0

    stop_loss = 0.98  # Stop loss at 98% of buy price
    take_profit = 1.02  # Take profit at 102% of buy price
    last_trade_time = time.time()
    start_time = time.time()

    print("Trading bot started.")
    while bot_running:
        if time.time() - start_time > 300:  # 5 minutes = 300 seconds
            print("Trading session timed out.")
            socketio.emit("bot_status", {"status": "completed"})
            break

        if time.time() - last_trade_time < 10:  # Reduced interval for testing
            time.sleep(1)
            continue

        live_price = fetch_live_price(pair)
        if not live_price:
            continue

        print(f"Live Price: {live_price}, Available Balance: {available_balance}")

        # If not holding, consider buying
        if not bought and available_balance >= trade_amount:
            strategy_signal = moving_average_crossover_strategy()
            print(f"Strategy Signal: {strategy_signal}")
            if strategy_signal == "buy":
                qty = trade_amount / live_price
                entry_price = live_price
                available_balance -= trade_amount
                bought = True
                trade_history.append({"action": "buy", "price": entry_price, "qty": qty})
                last_trade_time = time.time()
                print(f"Bought {qty:.6f} at ${entry_price:.2f}")

                socketio.emit("trade_update", {
                    "action": "buy",
                    "price": entry_price,
                    "profitLoss": 0,
                    "balance": available_balance
                })

        elif bought:
            if live_price >= entry_price * take_profit or live_price <= entry_price * stop_loss:
                profit_loss = (live_price * qty) - (entry_price * qty)
                available_balance += live_price * qty
                trade_history.append({"action": "sell", "price": live_price, "profitLoss": profit_loss})
                bought = False
                last_trade_time = time.time()
                print(f"Sold {qty:.6f} at ${live_price:.2f}, Profit/Loss: ${profit_loss:.2f}")

                socketio.emit("trade_update", {
                    "action": "sell",
                    "price": live_price,
                    "profitLoss": profit_loss,
                    "balance": available_balance
                })

    total_profit_loss = sum(
        trade.get("profitLoss", 0) for trade in trade_history if trade["action"] == "sell"
    )
    socketio.emit("trade_summary", {"total_profit_loss": total_profit_loss})
    print("Trading bot stopped.")


# Restart price simulation thread
def restart_price_simulation():
    global simulation_thread

    with thread_lock:
        stop_price_simulation.set()
        if simulation_thread and simulation_thread.is_alive():
            simulation_thread.join()

        stop_price_simulation.clear()
        simulation_thread = threading.Thread(target=simulate_price, daemon=True)
        simulation_thread.start()


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("change_currency")
def change_currency(data):
    global current_currency
    pair = data.get("currency", "bitcoin")
    if pair != current_currency:
        current_currency = pair
        print(f"Currency changed to: {current_currency}")
        restart_price_simulation()
        socketio.emit("clear_chart")


@socketio.on("start_bot")
def start_bot(data):
    global bot_running
    bot_running = True
    trade_amount = float(data.get("amount", 100))
    currency_pair = data.get("currency", current_currency)
    socketio.emit("bot_status", {"status": "active"})
    threading.Thread(target=trading_bot, args=(trade_amount, currency_pair), daemon=True).start()


@socketio.on("stop_bot")
def stop_bot():
    global bot_running
    bot_running = False

    total_profit_loss = sum(
        trade.get("profitLoss", 0) for trade in trade_history if trade["action"] == "sell"
    )
    socketio.emit("bot_status", {"status": "inactive"})
    socketio.emit("trade_summary", {"total_profit_loss": total_profit_loss})


if __name__ == "__main__":
    restart_price_simulation()
    socketio.run(app, debug=True)
