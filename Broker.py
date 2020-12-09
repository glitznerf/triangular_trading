# This Broker is supposed to connect to the Binance RUST API and get current market information
# All Binance requests return either a JSON object or an array
# The Binance API Docs are available here: https://binance-docs.github.io/apidocs

import requests

class Broker:
    def __init__(self, endpoint="https://api.binance.com/api/v3/"):
        self.endpoint = endpoint


    # Ping server to test connectivity
    def ping(self):
        test = requests.get(self.endpoint + "ping")
        if test.text == "{}":
            print("Success:", test.status_code, test.text)
        else:
            print("Failure:", test.status_code, test.text)


    # Get latest price for symbol, if empty symbol, returns prices for all symbols
    def get_price(self, symbol=""):

        # Protocol for all symbols
        if symbol == "":
            response = requests.get(self.endpoint + "ticker/price")
            if response.status_code == 200:
                print(response.json())
            elif response.status_code == 400:
                print(response.json()["msg"])
            else:
                print(response.status_code, response.text)

        # Protocol for specific symbols
        else:
            response = requests.get(self.endpoint + "ticker/price?symbol=" + symbol)
            info = response.json()
            if response.status_code == 200:
                price = info["price"]
                print(price)
            elif response.status_code == 400:
                print(info["msg"])
            else:
                print(response.status_code, response.text)


    # Get current average price for symbol
    def get_avg_price(self, symbol):
        response = requests.get(self.endpoint + "avgPrice?symbol=" + symbol)
        info = response.json()
        if response.status_code == 200:
            price = info["price"]
            print(price)
        elif response.status_code == 400:
            print(info["msg"])
        else:
            print(response.status_code, response.text)


    # Get orderbook information for symbol
    def orderbook(self, symbol, limit=500):
        response = requests.get(self.endpoint + "depth?symbol=" + symbol + "&limit=" + str(limit))
        info = response.json()
        if response.status_code == 200:
            print("bids:",info["bids"])
            print("asks:",info["asks"])
        elif response.status_code == 400:
            print(info["msg"])
        else:
            print(response.status_code, response.text)


# Tests:
B = Broker()
B.ping()
B.get_price("ETHBTC")
#B.get_price()
B.get_avg_price("ETHBTC")
B.orderbook("ETHBTC")
