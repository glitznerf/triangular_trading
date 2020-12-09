# A trading agent spotting arbitrage opportunities

from Broker import Broker

class Agent:
    def __init__(self, broker):
        self.broker = broker
        self.base = "EUR"
        self.pairs = []
        self.triangles = []


    # Print status of the Agent
    def status(self):
        print("Base currency", self.base)
        print("Broker OK") if self.broker.ping() else print("Broker not connected")
        print("Pairs OK") if len(self.pairs) != 0 else print("Pairs not set up")
        print("Triangles OK") if len(self.triangles) != 0 else print("Triangles not set up")


    # Get available currency pairs from broker and set up triangle structures
    # We set up base_currency -> b -> c -> base_currency
    # Returns: triangles (array of 3-tuples)
    def setup_pairs(self):
        symbols = self.broker.exchange_info()["symbols"]
        for symbol in symbols:
            if symbol["status"] == "TRADING":
                pair = symbol["baseAsset"], symbol["quoteAsset"]
                self.pairs.append(pair)
        for one in self.pairs:
            if self.base in one:
                b = one[0] if one[0] != self.base else one[1]
                for two in self.pairs:
                    if b in two and not self.base in two:
                        c = two[0] if two[0] != b else two[1]
                        for three in self.pairs:
                            if (self.base in three) and (c in three):
                                triangle = one,two,three
                                self.triangles.append(triangle)



# Tests
B = Broker()
A = Agent(B)
A.status()
A.setup_pairs()
print()
A.status()
