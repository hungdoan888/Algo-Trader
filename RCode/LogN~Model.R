# ===========================
#   
#   Author: Steven Cheng
#   Date: 12/09/2021
#   
#   The objective of this script is to automate the approximation of the
#   Log-Normal function distribution of the S&P 500. And then determine whether
#   shares that make up the S&P500 would be good buying opportunities using
#   probabilistic measures.
#
#   Variables to consider:
#   t = prediction time
#   n = interval (think SMA where we average over n periods)
#   F(Y,t,n) = distribution of the S&P500 at given time t over interval n
#   F(X,t,n) = distribution of X at given time t over interval n where X is an element of Y
#   BoS(F(X), F(Y)) = Buy Sell indicator
#   
#   Additional Resources:
#   R probability functions explained - https://thomasleeper.com/Rcourse/Tutorials/distributions.html
#
# ===========================

library("tidyverse")
library("readxl")
library("furrr")
library("tidyquant")

source("./Rcode/FinAlgoFuncs.R")

#### Import ####

SP500 <- read_rds("G:/My Drive/Individual Trading Stuff/MACD/output/priceTable/SP500List.rds") %>%
  mutate(., date = as.Date(date))

SPY <- tq_get("SPY", to = "2021-12-06", from = "2011-01-03")

N = 90 # averaging period
threshold = 0.50 # underperformance threshold

#### Working ####

# Variables to optimize. N controls the SD / rate of change. Threshold controls
# our tolerance levels. Possible implementation of ML here?
# Observations:
#   Greater N >> Smaller threshold window. 
#   Greater N >> Less trades being made (since swings are less likely to happen)

BSF <- SP500 %>% 
  select("date", "adjusted", "symbol") %>% 
  group_by(symbol) # %>% 
#  filter(., symbol == "AAPL")

S5 <- SPY %>% 
  select("date", "adjusted", "symbol") %>% 
  group_by(symbol)

BSF <- Fn_return_statistics(BSF, 90)
S5 <- Fn_return_statistics(S5, 90)

BSF <- Fn_XYreturn(BSF, S5) %>% group_by(symbol.x)
BSF_returns <- Fn_BuySell(BSF, 0.5)
BSF_returns_cleaned <- Fn_BuySell_Clean(BSF_returns)


#### Analysis | Results ####

# write.csv(BSF_returns_cleaned, "output/actionTable/NormalReturnBSI.csv")
# saveRDS(BSF_returns_cleaned, "output/actionTable/NormalReturnBSI.rds")

sum(BSF_returns_cleaned$Change[BSF_returns_cleaned$indicator == "SELL"], na.rm =TRUE) # Higher the number the better. Should never be negative

#fill with BS indicator and plot threshold line.
ggplot(filter(BSF_returns, symbol.x == "FOX"), aes(date, pXinY, colour = indicator)) + 
  geom_point() +
  geom_hline(aes(yintercept = threshold))

# Consider smoothing Buy and Sell.. i.e. if it's a series of BUY BUY BUY SELL
# BUY BUY, then it should all be BUY. Needs to be done without looking forward
# (since that would be impossible for day to day trading). Perhaps a second
# derivative indicator that can show "strength" of change for probability. 
#
# If something is sitting on the CUSP of being bought or sold, we should look at
# the second derivative to see how fast it is swinging between the two. If the
# derivative is close to 0 then it will ignore signal, if it's something greater
# than some threshold we consider it.


            