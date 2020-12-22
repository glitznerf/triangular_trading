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
    print(A.opportunities()[1][0][0])
    time.sleep(1)
