# A trading agent spotting arbitrage opportunities

from Broker import Broker
import time

class Agent:

    # Initialisation, NOTE: Adjust owned base currency and threshold
    def __init__(self, broker):
        self.broker = broker
        self.base = "USDT"
        self.fees = broker.get_fees()[1]
        self.profit_threshold = 0.0001


    # Print status of the Agent
    def status(self):
        print("Agent Status:")
        print(f"\tBase currency: {self.base}")
        print("\tBroker: OK") if self.broker.ping() else print("\tBroker: Not connected")
        print("\tFees: OK") if len(self.fees) != 0 else print("\tFees: Not set up")
        print(f"\tProfit Threshold: {self.profit_threshold}\n")

    # Calculate the relative outcome of the triangular trade indexed at one
    # Returns float
    def triangular_price(self, direction, order_prices, fees):
        base = 1.0
        for index, dir in enumerate(direction):
            if dir == "buy":
                base = (base * order_prices[index])
            else:
                base = base / order_prices[index]
            base = base - base*fees[index]
        return base

    # Calculate the maximum triangular trade quantities depending on the minimum
    # trade quantity of the three trades available.
    # Returns array of three floats
    def triangular_quantities(self, order_prices, direction, offered_quantities):
        a_1 = offered_quantities[0]*order_prices[1] if direction[1] == "buy" else offered_quantities[0]/order_prices[1]
        b_1 = offered_quantities[1]
        c_1 = offered_quantities[2]/order_prices[2] if direction[2] == "buy" else offered_quantities[2]*order_prices[2]

        if (a_1 < b_1) and (a_1 < c_1):
            a_2 = a_1*order_prices[2] if direction[2] == "buy" else a_1/order_prices[2]
            return [offered_quantities[0], a_1, a_2]
        elif (b_1 < a_1) and (b_1 < c_1):
            b_0 = b_1/order_prices[1] if direction[1] == "buy" else b_1*order_prices[1]
            b_2 = b_1*order_prices[2] if direction[2] == "buy" else b_1/order_prices[2]
            return [b_0, b_1, b_2]
        else:
            c_0 = c_1/order_prices[1] if direction[1] == "buy" else c_1*order_prices[1]
            return [c_0, c_1, offered_quantities[2]]


    # Parse prices from broker for arbitrage opportunities
    # Prints terminal message specifying exact trade opportunities
    def find_arbitrage(self):
        prices = self.broker.get_best_prices()
        logic_start_time = time.time()*1000
        A, B, C = self.base, "", ""
        direction = ["", "", ""]
        pairs = ["", "", ""]
        order_prices = [0, 0, 0]
        fees = [0, 0, 0]
        offered_quantities = [0, 0, 0]
        for i, (B, info) in enumerate(prices[A].items()):
            direction[0] = info[0]
            pairs[0] = info[1]
            order_prices[0] = info[2]
            ix = 0 if direction[0] == "buy" else 1
            fees[0] = self.fees[pairs[0]][ix]
            offered_quantities[0] = info[3]
            try:
                for i2, (C, info2) in enumerate(prices[B].items()):
                    direction[1] = info2[0]
                    pairs[1] = info2[1]
                    order_prices[1] = info2[2]
                    ix = 0 if direction[1] == "buy" else 1
                    fees[1] = self.fees[pairs[1]][ix]
                    offered_quantities[1] = info[3]

                    CA = prices[C][A]
                    direction[2] = CA[0]
                    pairs[2] = CA[1]
                    order_prices[2] = CA[2]
                    ix = 0 if direction[2] == "buy" else 1
                    fees[2] = self.fees[pairs[2]][ix]
                    offered_quantities[2] = CA[3]

                    effective_price = self.triangular_price(direction, order_prices, fees)
                    if effective_price > 1 + self.profit_threshold:
                        quantities = self.triangular_quantities(order_prices, direction, offered_quantities)
                        logic_end_time = time.time()*1000
                        print(f"\tLogic time: {logic_end_time - logic_start_time:.2f} ms")
                        message = ""
                        for i in range(3):
                            message += f"{direction[i]} {quantities[i]} of {pairs[i]} for {order_prices[i]}, "
                        print(f"For {(effective_price-1.0)*100.0:.4f}% profit, {message}")

            except KeyError:
                pass

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
