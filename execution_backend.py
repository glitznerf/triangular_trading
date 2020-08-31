class Broker:
    def __init__(self, api_key, signature, platform="Binance", api_url="https://api.binance.com/api/v3/"):
        self.api_key = api_key
        self.signature = signature
        self.platform = platform
        self.api_url = api_url

    def prices(self, *args):
        # Binance API get prices for *args
        return prices

    def volatility(self, *args):
        # Binance API get volatility for *args
        return vol

    def fees(self, *args):
        # Binance API get fees for *args
        return fees
