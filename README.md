# Spotting Triangular Trading Arbitrage Opportunities on Binance

## Quick Project Description
- **Idea:** Make three currency conversion trades and end up with a profit.  
- **Technologies:** Python3, Binance API.  
- **Status:** In development.  

## How Triangular Arbitrage Works
![Triangular](img/triangular.jpg)
The above graphic illustrates the process. Here, the system starts with 1000€, buys 0.032 BTC with an exchange rate of 0.000032, then buys 0.446 ETH with these BTC with an exchange rate of 13.9375 and finally buys 1022€ with these ETH with an exchange rate of 2,292.19. Disregarding transaction fees and time delay, this yields an instantaneous, risk-free net profit of 22€.  

These arbitrage opportunities occur regularly in the market, for a variety of reasons ranging from mistakes to a fast purposeful  liquidation of assets.  

## System Overview
![UML Diagram](img/uml.JPG)

We have two Python classes, Broker and Agent, for separation of concerns.

The Broker handles the interaction with the Binance Rust API and can be used to parse the API orderbook response into a python price dictionary from simple start to end currency with best-offer order price and quantity.  

The Agent implements the strategy, parsing the information passed on from the Broker to calculate profitable arbitrage opportunities. The Agent also accounts for trading fees and profit thresholding, prints the exact trade opportunities in the terminal and saves them to a local CSV database.  

*main.py* executes the trade logic and incorporates a delay to ensure compliant API behaviour.

## Results and Next Steps
![UML Diagram](img/hour_experiment.JPG)
After running the algorithm for one hour, the exemplary results can be summarized as follows:  
- **Number of Opportunities:** 38  
- **Relative Average Opportunity Profit:** 0.0878%  
- **Absolute Avgerage Opportunity Profit:** 1.1142 USDT  
- **Absolute Median Opportunity Profit:** 2.29E-06 USDT
- **Maximum Total Profit:** 42.3382 USDT

The major implementation problem to take advantage of these opportunities is time delay. When an opportunity arises, it closes within milliseconds. The process of buying cryptographic assets can take a settlement time of many minutes though, for example due to block mining time frame limitations. Another important time restriction comes from the API response time. While the parsing of the information and strategy takes single-digit milliseconds, the API request loop takes an average of around 400ms, with times regularly exceeding 1s. This could be a problem with either the connection, the Python requests library or the Binance API. Also, some opportunities might not actually be exploitable but rather be conversion errors.  

Therefore, the next steps are
1. Time delay optimization
2. Implement order placing
3. Develop risk management system
4. Test strategy live in spot markets
5. Create Dashboard for overview and results
6. Extend opportunity parsing to more than three trades (multi-angular over triangular)
