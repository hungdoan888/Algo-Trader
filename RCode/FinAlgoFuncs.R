#### ===========================
#   
#   Author: Steven Cheng
#   Date: 12/24/2021
#   
#   This script is to help breakout buy sell orders given some initial balance.
#   Inputs:
#     Table that denotes when to buy and sell
#     Table of prices
#     
#   Outputs:
#     Table that denotes when to buy and sell appended with how many shares
#     
# ===========================


#### Functions ####

Fn_return_statistics <- function(data, N, P = "adjusted"){
  # Consider updating to using geometric moving average rather than simple moving
  # average. Geometric will be better predictor for longer time horizons
  data <- tq_mutate(data, select = P, mutate_fun = periodReturn, period = "daily") %>%
    tq_mutate(., select = "daily.returns", col_rename = "SMA.return", mutate_fun = SMA, n = N) %>% 
    tq_mutate(., select = "daily.returns", col_rename = "SD.return", mutate_fun = runSD, n = N)
  
  return(data)
}

Fn_XYreturn <- function(X, Y){
  data <- left_join(X, Y, by = "date") %>% 
    mutate(., pXinY = pnorm(SMA.return.y, SMA.return.x, SD.return.x)) 
}

Fn_BuySell <- function(data, threshold = 0.5){
  
  # pXinY sets threshold for buying and selling. e.g. Given the distribution of
  # returns of X, we want to set a threshold x such that Pr(X=x) < E[Y]. As long
  # as the Pr(X = Y) < x then we will generate a BUY indicator. Else if the Pr(X = Y)
  # exceeds our threshold then we will generate a SELL indicator.
  #
  # For more clarity. lets say Y returns 1.02 and X is expected to return 1.03. If
  # the probability that X returns 1.02 is 40% and is greater than our threshold
  # of 35%, then we will Sell the shares as it would exceed our target probability
  # to be underperforming Y. The higher the threshold, the more extreme of returns
  # we are looking for. At the extrema, if we set our threshold to be 100% then we
  # would BUY regardless of the probabalistic performance of X relative to Y. If
  # we set the threshold to 0%, then we would always SELL since there is never a
  # 0 chance probability that X will perform at Y.
  
  data <- mutate(data, BS = if_else(pXinY <= threshold, 0, 1), indicator = if_else(pXinY <= threshold,"BUY", "SELL")) %>% 
    mutate(., Change = abs(c(NA, diff(BS, lag = 1))))
}

Fn_BuySell_Clean <- function(data) {
  data <- filter(data, Change == 1) %>% 
    mutate(., Change = c(NA, diff(adjusted.x, lag = 1)))
  
}

Fn_Reallocate <- function(data, date){
  # BUY -> append shares (i) to portfolio with 0 shares
  # count number of shares
  # DPS (dollar per share) Portfolio Value / N shares
  # shares = round_down(DPS / price@date)
  # if(dshares = shares_0 - shares > 0, sell dshares, buy dshares) 
  # CASH = CASH_0 - (price@date * dshares)
  # 
  # SELL -> -(symbol@date * shares)
  # CASH = -(-symbol@date * shares)
  # shares = 0
  
  
}

Fn_StockPriceAssign <-
  function(actionableTable,
           PriceTableL) {
    # 2 input - 1. actionableTable is the table of stocks and dates you want to
    # look up prices to. 2. stocklisting, is the subset list of stocks that we want
    # to grab from the actionableTable and assign prices to from PriceTableL
    AT.stocklisting <-
      left_join(actionableTable,
                PriceTableL,
                by = c("stock", "date"))
  }

Fn_StockPriceAssign2 <- function(actionableTable) {
  # 1 input version of the StockPriceAssign Function
  
  AT.stocklisting <-
    left_join(actionableTable,
              PriceTableL,
              by = c("stock" = "name", "date" = "date"))
}

Fn_CashFlow <- function(AT) {
  # converts buy and sells into cash flow. Consider buying N shares * Value at
  # time (t) a negative cash flow, and selling N shares as positive.
  AT.Cashflow <-
    ifelse(AT$action == "buy",
           AT$numberOfShares * AT$value * -1,
           AT$numberOfShares * AT$value * 1)
}

Fn_TickerTape <- function(AT) {
  # keeps count of N shares being bought and sold. 2 steps, one creating Inflow
  # and Outflow of shares based on "action", 2. grouping and summing over
  # shares.
  AT$Ticker <-
    ifelse(AT$action == "buy",
           AT$numberOfShares * 1,
           AT$numberOfShares * -1)
  
  AT$Ticker <-
    group_by(AT, stock) %>% mutate(., StockCount = cumsum(Ticker)) %>% ungroup(.)
}

Fn_OutstandingShares <- function(AT, curr_date){
  # Computes the number of shares outstanding from the actionableTable given a
  # current date. This relies on having run the TickerTape function on the table.
  # Note that this outputs a Table at curr_date
  OutstandingShares <- AT %>% group_by(., stock) %>% filter(date <= curr_date) %>% 
    summarise(., date = curr_date, stock = last(stock), OutstandingShares = last(StockCount)) %>% filter(., OutstandingShares>0)
}

Fn_OutstandingShares_Applied <- function(AT, date_list){
  # For future development to clean outstanding shares f(x) below that's manually done
}

Fn_Outstanding <- function(AT) {
  AT <- AT %>% group_by(.,date) %>% mutate(., OutstandingBal = last(Balance))
}

Fn_Balance_T <- function(AT,x){
  # Returns Balance from AT at time x
  BalT <- AT %>% filter(., date <= x) %>% filter(., date == max(.$date)) %>% select("date", "TotalBal")
  return(unique(BalT))
}
