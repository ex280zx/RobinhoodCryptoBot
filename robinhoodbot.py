import base64
import datetime
import json
import time
import uuid
from config import API_KEY, BASE64_PRIVATE_KEY
from cryptography.hazmat.primitives.asymmetric import ed25519
import requests

class CryptoAPITrading:
    def __init__(self):
        self.api_key = API_KEY
        private_bytes = base64.b64decode(BASE64_PRIVATE_KEY)
        self.private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_bytes[:32])
        self.base_url = "https://trading.robinhood.com"

    @staticmethod
    def _get_current_timestamp() -> int:
        return int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp())

    def make_api_request(self, method: str, path: str, body: str = ""):
        timestamp = self._get_current_timestamp()
        headers = self.get_authorization_header(method, path, body, timestamp)
        url = self.base_url + path
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=json.loads(body), timeout=10)
            response.raise_for_status()  # Raise an error for bad status codes
            return response.json()
        except requests.RequestException as e:
            print(f"Error making API request: {e}")
            return None

    def get_authorization_header(self, method: str, path: str, body: str, timestamp: int):
        message_to_sign = f"{self.api_key}{timestamp}{path}{method}{body}"
        signature = self.private_key.sign(message_to_sign.encode("utf-8"))
        return {
            "x-api-key": self.api_key,
            "x-signature": base64.b64encode(signature).decode("utf-8"),
            "x-timestamp": str(timestamp),
        }

    def get_best_bid_ask(self, symbol: str):
        path = f"/api/v1/crypto/marketdata/best_bid_ask/?symbol={symbol}"
        return self.make_api_request("GET", path)

    def place_limit_order(self, symbol: str, side: str, quantity: str, limit_price: str):
        order_body = {
            "symbol": symbol,
            "client_order_id": str(uuid.uuid4()),
            "side": side,
            "type": "limit",
            "limit_order_config": {
                "asset_quantity": quantity,
                "limit_price": limit_price,
                "time_in_force": "gtc"  # Good till canceled
            }
        }
        path = "/api/v1/crypto/trading/orders/"
        response = self.make_api_request("POST", path, json.dumps(order_body))
        return response

def monitor_doge():
    api_trading_client = CryptoAPITrading()
    trade_active = False
    last_reset_time = time.time()

    while True:
        try:
            # Step 1: Reset initial price if 5 minutes have passed without a trade
            if not trade_active and time.time() - last_reset_time > 300:  # 300 seconds = 5 minutes
                print("5 minutes passed without a trade, resetting initial price.")
                last_reset_time = time.time()

            # Get the initial price of DOGE
            initial_price_response = api_trading_client.get_best_bid_ask("DOGE-USD")
            initial_doge_price = float(initial_price_response['results'][0]['ask_inclusive_of_buy_spread'])
            print(f"Initial DOGE price recorded: {initial_doge_price}")

            while not trade_active:
                # Step 2: Get the current price of DOGE
                current_price_response = api_trading_client.get_best_bid_ask("DOGE-USD")
                current_doge_price = float(current_price_response['results'][0]['ask_inclusive_of_buy_spread'])
                print(f"DOGE current price: {current_doge_price}")

                # Step 3: Check for price drop and buy if conditions are met
                if current_doge_price < initial_doge_price * 0.9995:
                    print("Buying 1 DOGE due to price drop.")
                    buy_response = api_trading_client.place_limit_order("DOGE-USD", "buy", "1.0", str(current_doge_price))
                    print(f"Buy Response: {buy_response}")
                    trade_active = True  # Mark the trade as active

                    # Step 4: Monitor for selling conditions after buying
                    monitor_and_sell_doge(current_doge_price)
                    break

                time.sleep(3)  # Wait 3 seconds before checking the price again

            # After a trade is completed (either bought and waiting to sell or sold):
            if trade_active:
                print("Trade completed, waiting 5 minutes before resetting.")
                time.sleep(300)  # Wait 5 minutes before resetting and considering the next trade
                trade_active = False  # Reset trade activity status

        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(10)  # Wait a moment before trying again

def monitor_and_sell_doge(buy_price):
    api_trading_client = CryptoAPITrading()
    trade_active = True
    sell_buffer = 0.005  # 0.5% buffer

    while trade_active:
        current_price_response = api_trading_client.get_best_bid_ask("DOGE-USD")
        current_doge_price = float(current_price_response['results'][0]['bid_inclusive_of_sell_spread'])
        change = ((current_doge_price - buy_price) / buy_price) * 100
        print(f"DOGE current price: {current_doge_price}, Change from buy price: {change:.4f}%")

        # Sell if the price has increased by 0.5% from the buy price
        if change >= (sell_buffer * 100) and current_doge_price > buy_price:
            # Place a limit sell order at the current bid price
            print(f"Selling 1 DOGE due to price increase at {current_doge_price}.")
            sell_response = api_trading_client.place_limit_order("DOGE-USD", "sell", "1.0", str(current_doge_price))
            print(f"Sell Response: {sell_response}")
            trade_active = False  # Mark the trade as inactive
            break

        time.sleep(3)  # Check every 3 seconds

if __name__ == "__main__":
    monitor_doge()
