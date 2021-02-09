# AutoTrader Overview
Auto Trader automates stock option trading.

It consists of two components: 
- A server hosted in Google Cloud Platform (GCP) that parses text from a Discord bot for trade signals from selected options traders and analysts
- A locally hosted client that listens to the server for new trade signals and places validated orders with a TD Ameritrade brokerage account

AutoTrader is currently a functioning prototype and still in development.

## Installation

AutoTrader can be cloned from GitHub.


## Configuration
For AutoTrader Client configuration help see "docs/Setting Up AutoTrader Client.pdf"

## Using AutoTrader Client
1. Ensure you understand and have adjusted the brokerage order parameters in "config/order_guideslines.json"
- **Order Value** is the dollar-value upper limit to each individual order. 
- **Buy Limit Percentage** is used to calculate limit prices on a buy order. It represents how high above the signaled option contract price that a buy-limit order will be set. 
- **SL Percantage** is used to set stop-loss sell orders that accompany all buy orders. It represents the percentage below the signaled option price that a stop-market order will be set.  
2. Set your working directory to the auto_trader_client directory and run client.py
