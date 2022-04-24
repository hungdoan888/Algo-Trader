# Algorithmic Trading Application
- Created a trading bot that uses momentum indicators such as MACD and RSI to forecast S&P 500 stock prices
- Deployed application as a standalone executable with a graphic user interface capable of connecting to TD Ameritrade API to gather account information and place orders recommended by trading algorithm
- Incorporated back-tester used to assess model performance which was an 18% annualized return over 10 years

# Screenshots
![Alt text](/images/MACD_TDAmeritrade.JPG?raw=true "Screen shot of MACD connected to TD Ameritrade")
![Alt text](/images/Research.JPG?raw=true "Screen shot of Research Page")
![Alt text](/images/Simulator.JPG?raw=true "Screen shot of backtester/simulator page")

# Tech/framework used
- Python
- PyQt5
- cx-Freeze
- R

# Features
- Connects to TD Ameritrade API
- Shows account information such as stocks, shares, purchase prices for each stock, current market value, account value, and total cash
- Places buy and sell orders recommended by trading algorithm
- Allows users to research current stocks prices and provides visualizations
- Built in backtest that can be used to check any trading strategy; Visualization included which compares algorithm to SPY

