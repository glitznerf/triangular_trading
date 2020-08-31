import requests
from requests.exceptions import HTTPError

class Broker:
    def __init__(self, api_key, signature, platform="Binance", api_url="https://api.binance.com/api/v3/"):
        self.api_key = api_key
        self.signature = signature
        self.platform = platform
        self.api_url = api_url

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
                assert True==False
            except Exception as err:
                print("Error: ", err)
                assert True==False
        return prices

    def get_volatility(self, *args):
        # Binance API get volatility for *args
        vol = ""
        return vol

    def get_fees(self, *args):
        # Binance API get fees for *args
        fees = ""
        return fees


# Test
broker = Broker("","")
print(broker.get_prices("ETHBTC","BTCEUR"))
