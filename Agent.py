# A trading agent spotting arbitrage opportunities

from Broker import Broker
import time

class Agent:
    def __init__(self, broker):
        self.broker = broker
        self.base = "EUR"
        self.pairs = []
        self.triangles = []
        self.fees = broker.get_fees()[1]


    # Print status of the Agent
    def status(self):
        print("Agent Status:")
        print("  Base currency:", self.base)
        print("  Broker: OK") if self.broker.ping() else print("  Broker: Not connected")
        print("  Pairs: OK") if len(self.pairs) != 0 else print("  Pairs: Not set up")
        print("  Triangles: OK (" + str(len(self.triangles)) + ")") if len(self.triangles) != 0 else print("  Triangles: Not set up")
        print("  Fees: OK") if len(self.fees) != 0 else print("  Fees: Not set up")
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
    # ToDo: incorporate false broker response
    # Arguments: prices (dict), triangle (tuple)
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
                effective = effective / price - effective*self.fees.get(pairs[ix])[0]
            else:
                effective = effective * price - effective*self.fees.get(pairs[ix])[1]
        return effective, directions


    # Get dictionary of ticker prices by symbol
    # Returns: either (True, prices (dict)) or (False, False)
    def clean_prices(self):
        raw = self.broker.get_price()
        if raw[0]:
            prices = {}
            for entry in raw[1]:
                prices[entry["symbol"]] = float(entry["price"])
            return (True, prices)
        else:
            return (False, False)


    # Iterate over triangles and calculate effective prices for each, gather trading opportunities
    # ToDo: presentation, risk factor, profit threshold, liquidity metrics
    # Returns: either (True, opportunities in descending order (array), directions of trade (array)) or (False, False)
    def opportunities(self):
        assert len(self.triangles) > 0
        prices = self.clean_prices()
        directions = []
        if prices[0]:
            opportunities = []
            for triangle in self.triangles:
                effective, dir = self.eff_price(prices[1], triangle)
                if effective > 1:
                    opportunities.append((effective, triangle))
                    directions.append(dir)
            return (True, sorted(opportunities, reverse=True), directions)
        return (False, False)


    # Present a current opportunity confirmed with order book data
    # ToDo: Make orderbook info way more robust instead of simply taking top of orderbook!!
    # ToDo: get opportunities, calculate immediate execution prices backed by order book
    def opportunity(self):
        opps = self.opportunities()
        if opps[0]:
            # For each opportunity (trade idea), get the symbols and respective trade direction
            # Then get orderbook information, seek potential counterparty
            arbitrage = []
            for ix, opp in enumerate(opps[1][:5]):
                symbols = ["".join(opp[1][1][i]) for i in range(3)]
                prices = {}
                directions = opps[2][ix]
                for ix, symb in enumerate(symbols):
                    # If want to buy, get top of ask orderbook
                    if directions[ix]:
                        price = float(self.broker.orderbook(symb)[2][0][0])
                        prices[symb] = price
                    # If want to sell, get top of bid orderbook
                    else:
                        price = float(self.broker.orderbook(symb)[1][0][0])
                        prices[symb] = price
                effective_price, dir = self.eff_price(prices, opp[1])
                if effective_price > 1:
                    arbitrage.append([effective_price,opp[1]])
            if len(arbitrage) > 0:
                return (True, sorted(arbitrage, reverse=True)[0])

        return (False, False)
