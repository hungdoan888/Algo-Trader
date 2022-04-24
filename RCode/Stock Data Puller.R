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

setwd("C:/Users/Steven Cheng/Google Drive/Individual Trading Stuff/MACD") # Set this to your working directory

#### Importing List of S&P 500 Companies ####

SP500 <- tq_index("SP500")

#### Grabbing Historical Data of Companies off S&P 500 ####

StockList <- SP500$symbol
SP5List <- tq_get(StockList)
# Warnings, missing BRK.B, DG, MSI, BF.B -  okay though

write.csv(SP5List, "output/priceTable/SP500List.csv")
saveRDS(SP5List, "output/priceTable/SP500List.rds")

# SP5List<-read.csv("SP500List.csv") # run this if you just want to read it

# No longer needed since this is using xts package. The tidyquant package is much neater
# getSymbols(StockList[i])
# test <- get(StockList[1])[,6]
# test <- merge.xts(test, get(StockList[2])[,6])
# rm(StockList[i])


               