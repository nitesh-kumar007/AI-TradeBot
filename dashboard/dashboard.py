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
simulation_thread = None
stop_price_simulation = threading.Event()  # Event to signal stopping
thread_lock = threading.Lock()  # Lock for thread safety


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

    print(f"Started price simulation for {current_currency}")
    while not stop_price_simulation.is_set():
        live_price = fetch_live_price(current_currency)
        if live_price:
            last_price = live_price
        else:
            fluctuation = random.uniform(-0.5, 0.5)
            last_price *= 1 + (fluctuation / 100)

        current_time = time.strftime("%H:%M:%S")
        socketio.emit("price_update", {
            "price": round(last_price, 2),
            "time": current_time,
            "currency": current_currency
        })

        # Sleep for 2 seconds or exit early if stopped
        if stop_price_simulation.wait(2):
            break

    print(f"Stopped price simulation for {current_currency}")


def restart_price_simulation():
    global simulation_thread

    with thread_lock:
        # Signal any existing thread to stop
        stop_price_simulation.set()
        if simulation_thread and simulation_thread.is_alive():
            simulation_thread.join()  # Ensure the thread is fully stopped

        # Clear the stop signal and start a new thread
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

        # Restart the price simulation for the new currency
        restart_price_simulation()
        socketio.emit("clear_chart")  # Emit a signal to clear the chart


@socketio.on("start_bot")
def start_bot(data):
    global bot_running
    bot_running = True
    trade_amount = float(data.get("amount", 100))
    currency_pair = data.get("currency", "bitcoin")
    threading.Thread(target=trading_bot, args=(trade_amount, currency_pair), daemon=True).start()


@socketio.on("stop_bot")
def stop_bot():
    global bot_running
    bot_running = False


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


if __name__ == "__main__":
    restart_price_simulation()  # Start price simulation on server start
    socketio.run(app, debug=True)
