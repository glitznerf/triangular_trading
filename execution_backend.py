import requests
from requests.exceptions import HTTPError
from requests.auth import HTTPDigestAuth
import time

class Broker:
    def __init__(self, api_key, signature, platform="Binance", api_url="https://api.binance.com/api/v3/"):
        self.api_key = api_key
        self.signature = signature
        self.platform = platform
        self.api_url = api_url

    # Place order, return success as bool
    def order(self, symbol, amount, price):
        # Determine whether buy or sell order
        if amount > 0:
            side = "BUY"
        elif amount < 0:
            side = "SELL"
        else:
            return False

        # Execute order
        try:
            exec_time = int(time.time()*1000)
            exec = requests.post(self.api_url + "order", json = {"symbol": symbol,
                                                                "side": side,
                                                                "type": "limit",
                                                                "timeInForce": exec_time,
                                                                "quantity": amount,
                                                                "price": price,
                                                                "timestamp": int(time.time()*1000)},
                                                        auth=HTTPDigestAuth(self.api_key, self.signature))
            exec.raise_for_status()

            if exec.json()["status"] == "FILLED":
                return True
            else:
                i = 0
                while requests.get(self.api_url + (f"order?symbol={symbol}&orderId={exec.json()["clientOrderId"]}&timestamp={exec_time)}")).json()["status"] != "FILLED":
                    # Stop trying after one minute
                    if i == 60:
                        return False
                    time.sleep(1)
                    i += 1
                return True

        except HTTPError as http_err:
            print("HTTPError: ", http_err)
            return False

        except Exception as err:
            print("Error: ", err)
            return False

    # Get current market prices for symbols in *args
    def get_prices(self, *args):
        prices = []
        for arg in args:
            try:
                response = requests.get(self.api_url + (f"ticker/price?symbol={arg}"))
                response.raise_for_status()
                prices.append(response.json()["price"])
            except HTTPError as http_err:
                print("HTTPError: ", http_err)
                return False
            except Exception as err:
                print("Error: ", err)
                return False
        return prices

    def get_bias(self, *args):
        quantity, bias = [], []
        for arg in args:
            try:
                response = requests.get(self.api_url + (f"depth?symbol={arg}"))
                response.raise_for_status()
                quant_bid = 0.0
                quant_ask = 0.0
                for bid in response.json()["bids"]:
                    quant_bid += float(bid[1])
                for ask in response.json()["asks"]:
                    quant_ask += float(ask[1])
                quantity.append(quant_bid+quant_ask)
                bias.append(quant_bid-quant_ask)
            except HTTPError as http_err:
                print("HTTPError: ", http_err)
                return False
            except Exception as err:
                print("Error: ", err)
                return False
        return quantity, bias

    def get_fees(self, *args):
        # Binance API get fees for *args
        fees = ""
        return fees


# Test
broker = Broker("","")
print(broker.get_prices("ETHBTC","BTCEUR"))
