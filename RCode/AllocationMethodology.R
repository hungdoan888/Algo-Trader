# ===========================
#   
#   Author: Steven Cheng
#   Date: 12/18/2021
#   
#   This script is to help breakout buy sell orders given some initial balance.
#   Inputs:
#     Table that denotes when to buy and sell
#     Table of prices
#     
#   Outputs:
#     Table that denotes when to buy and sell appended with how many shares
#     
# ===========================s

library("tidyverse")
library("readxl")
library("furrr")
library("tidyquant")
library("lubridate")

source("./Rcode/FinAlgoFuncs.R")

#### Import ####

BSF_returns_cleaned<-readRDS("output/actionTable/NormalReturnBSI.rds") %>% 
  rename("stock.x" = "symbol.x")
SP500 <- read_rds("G:/My Drive/Individual Trading Stuff/MACD/output/priceTable/SP500List.rds") %>% 
  mutate(., date = as.Date(date)) %>% 
  rename("stock" = "symbol") 

Init_Balance = 100000

date_list <- SP500$date %>% 
  unique(.)# %>% 
#  {as.Date(c(min(.):max(.)))}


#### Working ####

# Flat Asset Allocation

# Take some percentage of initial balance - buy n shares rounded down to nearest whole number.

Portfolio <- tibble_row("CASH", Init_Balance) 
colnames(Portfolio) <- c("stock", "shares")
# Portfolio <- add_row(Portfolio, stock = "AAPL",shares = 1500) %>% 
#  add_row(., stock = "HD", shares = 3)

ActionTable <-
  as_tibble(matrix(ncol = 5, nrow = 0), .name_repair = make.names)
colnames(ActionTable) <- c("stock", "assignment_date", "indicator", "shares", "assignment_price")
ActionTable <-
  mutate(
    ActionTable,
    stock = as.character(stock),
    assignment_date = as.Date(assignment_date),
    indicator = as.character(indicator),
    shares = as.numeric(shares),
    assignment_price = as.numeric(assignment_price)
  )


BSF <- BSF_returns_cleaned %>% ungroup(.) %>% 
  arrange(., date) %>%
  select("date", "stock.x", "adjusted.x", "indicator") %>%
  rename("stock" = "stock.x", "adjusted" = "adjusted.x")
#  filter(., stock %in% c("BSX", "EBAY")) %>% 
#  filter(.,  date >= "2011-05-31" & date <"2011-06-30")

date_vector <- match(BSF$date, date_list)

BSF$assignment_date <- date_list[date_vector+1]

BSF <- left_join(BSF, SP500, by = c("stock", "assignment_date" = "date")) %>%
  select("date", "stock", "adjusted.x", "indicator", "assignment_date", "adjusted.y") %>% 
  rename("adjusted" = "adjusted.x", "assignment_price" = "adjusted.y")


begin_date <- match(min(BSF$date), date_list)
end_date <- match(max(BSF$date), date_list)

# Consider parallelization using foreach package

for(i in 0:(end_date - begin_date)){
  print(date_list[begin_date+i])

#### Sell Processing ####

BSF_date <- filter(BSF, date == date_list[begin_date + i] & indicator == "SELL")

y <- full_join(Portfolio, BSF_date, by = "stock") %>% 
  mutate(., sale = shares * assignment_price)

y[1, 2] <- sum(c(Portfolio[[2]][1], y$sale), na.rm=TRUE)

Portfolio <- y %>% filter(is.na(indicator)) %>% select("stock", "shares")

ActionTable <- y %>% filter(!is.na(sale)) %>%
  select("stock", "assignment_date", "indicator", "shares", "assignment_price") %>% 
  bind_rows(ActionTable, .)
  


#### Buy Processing ####

BSF_date <- filter(BSF, date == date_list[begin_date + i] & indicator == "BUY")

y <- full_join(Portfolio, BSF_date, by = "stock") %>% 
  mutate(., assignment_date = max(assignment_date, na.rm = TRUE)) %>% 
  left_join(., SP500, by = c("stock", "assignment_date" = "date")) %>%
  select("stock", "shares","date", "adjusted.x", "indicator", "assignment_date", "adjusted.y") %>% 
  rename("adjusted" = "adjusted.x", "assignment_price" = "adjusted.y") %>% 
  replace_na(., list(shares = 0)) %>% 
  mutate(., sale = shares * assignment_price)

y[1,2] <- sum(c(y[[2]][1], y$sale), na.rm=TRUE)
PPS <- y[[2]][1] / length(y$stock[-1])

y <- mutate(y, new_shares = floor(PPS/assignment_price), indicator = if_else(new_shares - shares>=0, "BUY", "SELL"))

Portfolio <-
  transmute(y,
            stock = stock,
            shares = if_else(!is.na(new_shares),
                             new_shares,
                             shares))

Portfolio[1,2] <- sum(c(y[[2]][1], -y$new_shares*y$assignment_price), na.rm=TRUE)

ActionTable <- y %>% filter(!is.na(new_shares)) %>% 
  mutate(., shares = abs(new_shares - shares)) %>%
  select("stock", "assignment_date", "indicator", "shares", "assignment_price") %>% 
  bind_rows(ActionTable, .)

print(Portfolio[[2]][1])


}

ActionTable <- filter(ActionTable, shares != 0)

colnames(ActionTable) <- c("stock", "date", "action", "numberOfShares")

ActionTable <-  mutate(ActionTable, action = if_else(action == "BUY", "buy", "sell"))%>% select(., 1:4) 

write.csv(ActionTable, "./output/actionTable/EvenAllocation.csv", row.names = FALSE)
saveRDS(ActionTable, "./output/actionTable/EvenAllocation.rds")

SP5 <- SP500 %>% filter(., date == max(SP500$date))

Portfolio <- left_join(Portfolio, SP5, by = c("stock"))

x<-sum(c(Portfolio[[2]][1], Portfolio$shares*Portfolio$adjusted), na.rm = TRUE)

x - 100000*453.42/103.11

exp(log(x/Init_Balance)/time_length(max(date_list)-min(date_list), "years"))

exp(log(453.42/103.11)/time_length(max(date_list)-min(date_list), "years"))


