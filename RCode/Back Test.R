# ===========================
#   
#   Author: Steven Cheng
#   Date: 12/05/2021
#   
#   Q1: Profitable?
#   Q2: Balance(t)?
#   Q3: Assume B(0) = 100k, what is B(t)?
#
# ===========================

# install.packages("tidyverse") # only if needed
# install.packages("furrr")

library("tidyverse")
library("readxl")
library("googlesheets4")
library("furrr")

source("./Rcode/FinAlgoFuncs.R")

#### Initialization ####

plan(multisession, workers = length(availableWorkers()) -2) # This is for parallel processing

# Setting initial balance
init_balance = 100000

#### Data Import ####

# Buy & Sell Data 
actionableTable <- read.csv("./output/actionTable/actionTable.csv") %>%
  filter(., numberOfShares >0)

# Price Data
PriceTable <- read.csv("./output/priceTable/priceTable.csv") %>% 
  rename("stock" = "name")

# Pivoting Price table to make it easier to use "Join" functions. Also setting date to a "date" format
PriceTableL <- pivot_longer(PriceTable , cols = 2:length(colnames(PriceTable))) %>% mutate(., date = as.Date(date))


#### Working ####

# Passing list of all unique stock tickers to assign prices from Actionable Table
Stock_Grab <- Fn_StockPriceAssign(actionableTable, PriceTableL)

# Creating Cash Flows due to buy / sell  orders
Stock_Grab$CF <- Fn_CashFlow(Stock_Grab)

# Taking initial balance and summing through cash flows
Stock_Grab <- mutate(Stock_Grab, Balance = (cumsum(CF)+init_balance))

# Running through the TickerTape Function to track buys and sells of shares
Stock_Grab <- Fn_TickerTape(Stock_Grab)

Stock_Grab <- Fn_Outstanding(Stock_Grab)


# Outstanding Shares f(x) - where OS represents "Outstanding Shares" and OV represents "Outstanding Value"
# The below works but takes too long for a loop

UniqueDates <- unique(Stock_Grab$date)
d<-length(unique(Stock_Grab$date))
test <- as.tibble(x = 1:d)

for(i in as.list(1:d)){
  test$date[i] = as.character(UniqueDates[i])
  test$OS[[i]] <- as.tibble(Fn_OutstandingShares(Stock_Grab, UniqueDates[i]))
#  test$OS[[i]] <- Fn_StockPriceAssign(test$OS[[i]], test$OS[[i]]$stock) # no longer needed as these can be handled through more efficient apply functions below
#  test$OV[i] <- summarise(test$OS[[i]], sum(OutstandingShares*value))  # no longer needed as these can be handled through more efficient apply functions below
  print(i/d)
}

#This works below somehow? should consider adding parallel processing to make it go faster.
test[[3]] <- future_map(test[[3]], Fn_StockPriceAssign2, .progress = TRUE)
test$OV <- unlist(map(test[[3]], summarise, sum(OutstandingShares*value)))

test$date <- as.Date(test$date)

Stock_Grab <- left_join(Stock_Grab, test, by = c("date"))

Stock_Grab$OV <- unlist(Stock_Grab$OV)

Stock_Grab <- Stock_Grab %>%
  mutate(., TotalBal = OutstandingBal + OV) %>% ungroup(.)

attributes(StockGrab[c("TotalBal","OV")]) <- NULL
  
# # Grabbing final values per share (SC: 12/7/21 this code has been made redundant by the Outstanding shares f(x))
# Stock_Grab2 <-
#   Stock_Grab %>% group_by(., stock) %>% filter(date == max(date)) %>% group_by(., date) %>%
#   mutate(EquityBalance = sum(EquityValue)) %>% filter(StockCount > 0)

#### Results ####

# Balance v Time
ggplot(Stock_Grab, aes(date, TotalBal)) + 
  geom_line() + 
  geom_line(aes(date, OutstandingBal), color = "red") + 
  geom_line(aes(date, OV), color = "green")

Fn_Balance_T(Stock_Grab, "2021-9-01")

