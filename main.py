# The main execution of the program

import Broker
import Agent


# Init and set up Broker and Agent
B = Broker()
A = Agent(B)
A.setup_pairs()
A.status()


# A simple opportunity ticker
while True:
    print(A.opportunities()[0])
    time.sleep(1)
