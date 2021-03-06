# This Broker is supposed to connect to the Binance RUST API and get current market information
# All Binance requests return either a JSON object or an array
# The Binance API Docs are available here: https://binance-docs.github.io/apidocs

import requests
import time
import hmac
import hashlib
import urllib
import json
import numpy as np

class Broker:

    # Initialisation - NOTE: please adjust API-Key and SecretKey
    def __init__(self):
        self.url = "https://api.binance.com/"
        self.endpoint = self.url + "api/v3/"
        self.userendpoint = self.url + "wapi/v3/"
        self.apikey = ""
        self.secretkey = ""
        self.symbols = {}
        self.get_symbols()


    # Ping server to test connectivity.
    # Returns True if successful, False if unsuccessful
    def ping(self):
        try:
            test = requests.get(self.endpoint + "ping")
            return True if test.text == "{}" else False
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

    # Get best price for symbol, if empty symbol, returns prices for all symbols
    # Argument: Ticker symbol (str) (optional)
    # Returns (True, price(s)) or (False, error_message)
    def get_raw_best_price(self, symbol=""):
        response = 0

        if symbol == "":
            response = requests.get(self.endpoint + "ticker/bookTicker")
        else:
            response = requests.get(self.endpoint + "ticker/bookTicker?symbol=" + symbol)

        if response.status_code == 200:
            return (True, response.json())
        elif response.status_code == 400:
            return (False, response.json()["msg"])
        else:
            return (False, response.text)

    # Get best prices in dictionary form
    # Returns dictionary of form price[owned_currency][new_currency]
    # Dictionary entry contains direction, symbol, price and quantity
    def get_best_prices(self):
        api_start_time = time.time()*1000
        raw_best_price = self.get_raw_best_price()[1]
        api_end_time = time.time()*1000
        print(f"\tAPI Time: {api_end_time - api_start_time:.2f} ms")
        parsing_start_time = time.time()*1000
        price = {}
        for ticker in raw_best_price:
            symbol = ticker["symbol"]
            try:
                symbol_a, symbol_b = self.symbols[symbol]
            except KeyError:
                continue
            buy = ["buy", symbol, float(ticker["bidPrice"]), float(ticker["bidQty"])]
            sell = ["sell", symbol, float(ticker["askPrice"]), float(ticker["askQty"])]
            if buy[2] != 0:
                try:
                    price[symbol_b][symbol_a] = buy
                except KeyError:
                    price[symbol_b] = {}
                    price[symbol_b][symbol_a] = buy
            if sell[2] != 0:
                try:
                    price[symbol_a][symbol_b] = sell
                except KeyError:
                    price[symbol_a] = {}
                    price[symbol_a][symbol_b] = sell
        parsing_end_time = time.time()*1000
        print(f"\tParsing Time: {parsing_end_time - parsing_start_time:.2f} ms")
        return price


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


    # Get fee information
    # Returns either (True, fees (maker/taker, percent, dict)) or (False)
    def get_fees(self):
        params = urllib.parse.urlencode({
            "signature" : hmac.new(self.secretkey.encode('utf-8'), "".encode("utf-8"), hashlib.sha256).hexdigest(),
            "timestamp" : int(time.time() * 1000)})

        response = requests.get(self.userendpoint + "tradeFee.html",
            params = params,
            headers = {
                "X-MBX-APIKEY" : self.apikey,
            })

        if response.status_code == 200:
            fees = {}
            for symbol in response.json()["tradeFee"]:
                fees[symbol["symbol"]] = [symbol["maker"], symbol["taker"]]
            return (True, fees)
        else:
            return (False)

    # Get all available symbols, excluding discontinued "NGN"s
    def get_symbols(self):
        response = requests.get(self.endpoint + "exchangeInfo")
        info = response.json()
        for entry in info["symbols"]:
            symbol = entry["symbol"]
            symbol_a = entry["baseAsset"]
            symbol_b = entry["quoteAsset"]
            if not (symbol_b == "NGN" and not (symbol_a == "BTC" or symbol_a == "USDT")):
                self.symbols[symbol] = [symbol_a, symbol_b]
