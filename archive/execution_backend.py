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
        self.fees = {}                  # Needs manual entering

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
                clientOrderId = exec.json()["clientOrderId"]
                while requests.get(self.api_url + f"order?symbol={symbol}&orderId={clientOrderId}&timestamp={exec_time}").json()["status"] != "FILLED":
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

    # Get current order book buy/sell bias
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
                if quant_bid-quant_ask > 0:
                    bias.append(quant_bid/quant_ask)
                else:
                    bias.append(-quant_bid/quant_ask)
            except HTTPError as http_err:
                print("HTTPError: ", http_err)
                return False
            except Exception as err:
                print("Error: ", err)
                return False
        return quantity, bias

    # Get the trading fees for symbols in args
    def get_fees(self, *args):
        fees = []
        for arg in args:
            fees.append(self.fees.get(arg))
        return fees

# Executer runs the strategy
class Executer:
    def __init__(self, params=[0,0],currencies_a=[], currencies_b=[], currencies_c=[]):
        self.params = params
        self.currency_pairs = []
        for a in currencies_a:
            for b in currencies_b:
                for c in currencies_c:
                    self.currency_pairs.append([a,b,c])
        self.API = Broker("","")

    # Run triangular trading: scan for signal, execute trade
    def run_triangular(self, standard_amount=50, timeout=5):    # standard_amount in Euro, timeout in minutes
        init_time = int(time.time()*1000)
        # During runtime
        while (int(time.time()*1000) < int(init_time + timeout*60000)):
            # Loop over currency pairs
            for c_pair in currency_pairs:
                a, b, c = c_pair
                prices = self.API.get_prices(a+b, b+c, c+a, "EUR"+b)
                price = prices[0]*prices[1]*prices[2]
                vol = self.API.get_bias(a+b, b+c, c+a)
                fee_ = self.API.get_fees(a+b, b+c, c+a)
                fee = 1/((1+fee_[0])*(1+fee_[1])*(1+fee_[2]))
                risk = 1/(params[0]*abs(vol) + p[1] + 1)

                # Generate signal
                indicator = price*fee*risk
                if indicator > 1:
                    net_profit = (price*fee-1)*100
                    risk_factor = 1/risk
                    print(f"Buy {a+b,b+c,c+a} for an expected net profit of {net_profit}% and a risk factor of {risk_factor}.")
                    amount = standard_amount*prices[3]
                    if self.API.order(a+b, amount, prices[0]):
                        print(f"Order {a+b} executed!")
                        if self.API.order(b+c, amount*prices[1], prices[1]):
                            print(f"Order {b+c} executed!")
                            if self.API.order(c+a, amount*prices[1]*prices[2], prices[2]):
                                print(f"Order {c+a} executed! Triangular trade completed. \n\n")
                            else:
                                print(f"Order {c+a} NOT executed!")
                                error_alert()
                        else:
                            print(f"Order {b+c} NOT executed!")
                            error_alert()
                    else:
                        print(f"Order {a+c} NOT executed!")
                        error_alert()

    # Notify of error, cancel trades/positions at risk
    def error_alert(self):
        pass

# Test
broker = Broker("","")
print(broker.get_prices("ETHBTC","BTCEUR"))
