# ===========================
#   
#   Author: Steven Cheng
#   Date: 12/07/2021
#   
# Objectives: To understand a series of tools that will help retrieve stock
# prices and perform stock price analysis
# 
# ===========================

# install.packages("tidyquant")
# install.packages("finreportr")
library("finreportr")
library("tidyquant")
library("tidyverse")
library("googlesheets4")
library("reticulate")

#### Getting Real Time Quotes ####

# This is using the quantmod package
getQuote("AAPL")
getQuote("QQQQ;SPY;^VXN",what=yahooQF())
Stocklist <- c("AAPL", "QQQQ", "SPY", "CMG")
getQuote(Stocklist, what=standardQuote()[[1]])
getQuote(Stocklist, )

# This is using the tidyquant package
tq_get("AAPL")
tq_index("SP500") # Pulls the entire S&P500 list


#### Pulling Stock & Historical Data ####

getSymbols('IBM',src='yahoo')

#### Pulling Option Chains ####

AAPL <- getOptionChain("AAPL")
tq_get_options("AAPL")

#### Financial Statements ####

# This needs to be looked further into

#### Charting ####

chartSeries(IBM)
addBBands()
addSMA()

getSymbols('SBUX')
barChart(SBUX)
addTA(EMA(Cl(SBUX)), on=1, col=6)
addTA(OpCl(SBUX), col=4, type='b', lwd=2)
# create new EMA TA function
newEMA <- newTA(EMA, Cl, on=1, col=7)
newEMA()
newEMA(on=NA, col=5)

getSymbols(c('AAPL','SBUX', 'CMG', 'F')) 

#### PYTHON ####

source_python("./Rcode/test_func.py") # This works
