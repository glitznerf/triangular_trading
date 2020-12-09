# This Broker is supposed to connect to the Binance RUST API and get current market information
# All Binance requests return either a JSON object or an array
# The Binance API Docs are available here: https://binance-docs.github.io/apidocs

import requests
import time

class Broker:
    def __init__(self, endpoint="https://api.binance.com/api/v3/"):
        self.endpoint = endpoint


    # Ping server to test connectivity.
    # Returns True if successful, False if unsuccessful
    def ping(self):
        try:
            test = requests.get(self.endpoint + "ping")
            if test.text == "{}":
                return True
            else:
                return False
        except:
            return False


    # Get latest price for symbol, if empty symbol, returns prices for all symbols
    # Argument: Ticker symbol (str) (optional)
    # Returns (True, price(s)) or (False, error_message)
    def get_price(self, symbol=""):
        response = 0

        if symbol == "":
            response = requests.get(self.endpoint + "ticker/price")
        else:
            response = requests.get(self.endpoint + "ticker/price?symbol=" + symbol)

        if response.status_code == 200:
            return (True, response.json())
        elif response.status_code == 400:
            return (False, response.json()["msg"])
        else:
            return (False, response.text)


    # Get current average price for symbol
    # Argument: Ticker symbol (str)
    # Returns (True, price) or (False, error_message)
    def get_avg_price(self, symbol):
        response = requests.get(self.endpoint + "avgPrice?symbol=" + symbol)
        if response.status_code == 200:
            return (True, response.json()["price"])
        elif response.status_code == 400:
            return (False, response.json()["msg"])
        else:
            return (False, response.text)


    # Get orderbook information for symbol
    # Arguments: Ticker symbol (str), max number of orders (int) (optional)
    # Returns (True, bids, asks) or (False, error_message)
    def orderbook(self, symbol, limit=500):
        response = requests.get(self.endpoint + "depth?symbol=" + symbol + "&limit=" + str(limit))
        info = response.json()
        if response.status_code == 200:
            return (True, info["bids"], info["asks"])
        elif response.status_code == 400:
            return (False, info["msg"])
        else:
            return (False, response.text)


    # Get Exchange information
    # Returns either (True, information (json)) or (False)
    def exchange_info(self):
        response = requests.get(self.endpoint + "exchangeInfo")
        if response.status_code == 200:
            return (True, response.json())
        else:
            return (False)


# Tests:
#symbol = "ETHBTC"
#B = Broker()
#print(B.ping())
#print("")
#print(B.get_price(symbol))
#print("")
#print(B.get_price())
#print("")
#print(B.get_avg_price(symbol))
#print("")
#print(B.orderbook(symbol))
#print("")

#print(f"  A simple price ticker for {symbol}")
#for i in range(20):
#    print(B.get_price(symbol))
#    time.sleep(1)
