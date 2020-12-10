# A trading agent spotting arbitrage opportunities

from Broker import Broker
import time

class Agent:
    def __init__(self, broker):
        self.broker = broker
        self.base = "EUR"
        self.pairs = []
        self.triangles = []


    # Print status of the Agent
    def status(self):
        print("Agent Status:")
        print("  Base currency:", self.base)
        print("  Broker: OK") if self.broker.ping() else print("  Broker: Not connected")
        print("  Pairs: OK") if len(self.pairs) != 0 else print("  Pairs: Not set up")
        print("  Triangles: OK (" + str(len(self.triangles)) + ")") if len(self.triangles) != 0 else print("  Triangles: Not set up")
        print("")


    # Get available currency pairs from broker and set up triangle structures
    # We set up base_currency -> b -> c -> base_currency
    # Returns: triangles (array of 3-tuples)
    def setup_pairs(self):
        exchange_info = self.broker.exchange_info()
        if exchange_info[0]:
            symbols = exchange_info[1]["symbols"]
            for symbol in symbols:
                if symbol["status"] == "TRADING":
                    pair = symbol["baseAsset"], symbol["quoteAsset"]
                    self.pairs.append(pair)
            for one in self.pairs:
                if self.base in one:
                    b = (one[0] if one[0] != self.base else one[1])
                    for two in self.pairs:
                        if b in two and not self.base in two:
                            c = (two[0] if two[0] != b else two[1])
                            for three in self.pairs:
                                if (self.base in three) and (c in three):
                                    triangle = one, two, three
                                    self.triangles.append(((b,c),triangle))


    # Calculate effective triangular price
    # ToDo: incorporate fees
    # ToDo: incorporate false broker response
    # Arguments: prices (json), triangle (tuple)
    # Returns: effective price (float)
    def eff_price(self, prices, triangle):
        pairs = ["".join(pair) for pair in triangle[1]]
        prices = [prices[pair] for pair in pairs]
        directions = []
        for ix, curr in enumerate([self.base, triangle[0][0], triangle[0][1]]):
            directions.append(True if curr == triangle[1][ix][1] else False)
        effective = 1
        for ix, price in enumerate(prices):
            if directions[ix]:
                effective = effective *price
            else:
                effective = effective / price
        return effective


    # Get dictionary of ticker prices by symbol
    # Returns: either (True, prices (dict)) or (False)
    def clean_prices(self):
        raw = self.broker.get_price()
        if raw[0]:
            prices = {}
            for entry in raw[1]:
                prices[entry["symbol"]] = float(entry["price"])
            return (True, prices)
        else:
            return (False)


    # Iterate over triangles and calculate effective prices for each, gather trading opportunities
    # ToDo: presentation, risk factor, profit threshold, liquidity metrics
    # Returns: either (True, opportunities in descending order (array)) or (False)
    def opportunities(self):
        assert len(self.triangles) > 0
        prices = self.clean_prices()
        if prices[0]:
            opportunities = []
            for triangle in self.triangles:
                effective = self.eff_price(prices[1], triangle)
                if effective > 1:
                    opportunities.append((effective, triangle))
            return (True, sorted(opportunities, reverse=True))
        return (False)


    # Present a current opportunity confirmed with order book data
    # ToDo: get opportunities, calculate immediate execution prices backed by order book
    def opportunity(self):
        pass



# Tests
B = Broker()
A = Agent(B)
A.setup_pairs()
A.status()

while True:
    print(A.opportunities()[0])
    time.sleep(1)
