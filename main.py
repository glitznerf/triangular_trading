# The main execution of the program

from Broker import Broker
from Agent import Agent
import time


# Init and set up Broker and Agent
B = Broker()

A = Agent(B)
A.setup_pairs()
A.status()


# A simple opportunity ticker
while True:
    opp = A.opportunity()
    if opp[0]:
        print("Arbitrage opportunity with base", opp[1][0])
        print("  Exchange", opp[1][1][1][0], "->", opp[1][1][1][1], "->", opp[1][1][1][2], "\n")
    else:
        print(" ")
    #print(float(B.orderbook("ADAEUR")[1][0][0]))
    time.sleep(1)
