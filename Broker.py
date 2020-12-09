# This Broker is supposed to connect to the Binance RUST API and get current market information
# All Binance requests return either a JSON object or an array
# The Binance API Docs are available here: https://binance-docs.github.io/apidocs

import requests

class Broker:
    def __init__(self, endpoint="https://api.binance.com"):
        self.endpoint = endpoint

    # Ping server to test connectivity
    def ping(self):
        r = requests.get(self.endpoint + "/api/v3/ping")
        if r.text == "{}":
            print("Success:", r.status_code, r.text)
        else:
            print("Failure:", r.status_code, r.text)

    # Get current average price for symbol
    def get_price(self, symbol):
        pass

    # Get orderbook information for symbol


# Tests:
B = Broker()
B.ping()
