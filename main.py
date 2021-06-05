# The main execution of the program

from Broker import Broker
from Agent import Agent
import time


# Init and set up Broker and Agent
B = Broker()
A = Agent(B)
A.status()

# Simple arbitrage opportunity tracker
while True:
    A.find_arbitrage()
    time.sleep(1)
