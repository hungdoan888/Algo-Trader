# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 07:57:03 2021

@author: hungd
"""

#%% Imports

from addPaths import addPaths
addPaths()
import os
import time
import pandas as pd
from datetime import datetime as dt
from MACDTradingStrategy import pridictBuySellWithMACD
from simulateReturns2 import simulateReturnsExact

#%% For Testing

# MACDTradingStrategy
listOfStockToTradeFile = r"C:\Users\hungd\Desktop\MACD\MACD\constituents\constituents_csv.csv"
start = "2009-12-09"
end = "2021-12-02"
shortMACD = 12  # Short EMA
longMACD = 26  # Long EMA
signalMACD = 9  # Signal
rewardRiskRatio = 2.5  # risk: reward
diversification = 0.03  # Maximum allowable percentage of a single stock in entire portfolio
stopLossWhenInf = 0.95  # Percent of Adj closing price value at time of buy
diamondHands = False  # If true, once profit target is exceed, don't sell until first close price < close price of prev day
output = r"C:\Users\hungd\Desktop\MACD\MACD\output"

# Simulate exact returns
actionTable = output + r"\actionTable\\actionTable.csv"
priceTable = output + r"\priceTable\\priceTable.csv"
initialBalance = 100000
importCustomPriceTable = True

#%% Suppress slicing warnings

pd.options.mode.chained_assignment = None  # default='warn'

#%% Create Results, price, and action folders if they do not exist

def createDirs():
    # Paths
    actionPath = output + r"\actionTable"
    pricePath = output + r"\priceTable"
    resultsPath = output + r"\results"
    
    # Action
    if not os.path.exists(actionPath):
        os.makedirs(actionPath)
        
    # Price
    if not os.path.exists(pricePath):
        os.makedirs(pricePath)
        
    # Results
    if not os.path.exists(resultsPath):
        os.makedirs(resultsPath)
        
#%% Get results for all stocks

def resultsForStocks(df_resultsByTradeNum, stock):
    
    # Create temp df
    numberOfTrades = len(df_resultsByTradeNum)
    totalDaysTraded = df_resultsByTradeNum["daysTraded"].sum()
    numberOfWinningTrades = df_resultsByTradeNum["totalProfitPerTrade"][df_resultsByTradeNum["totalProfitPerTrade"] >= 0].count()
    numberOfLosingTrades = numberOfTrades - numberOfWinningTrades
    winPercentage = numberOfWinningTrades / numberOfTrades
    profitFromWinners = df_resultsByTradeNum["totalProfitPerTrade"][df_resultsByTradeNum["totalProfitPerTrade"] >= 0].sum()
    lossesFromLosers = df_resultsByTradeNum["totalProfitPerTrade"][df_resultsByTradeNum["totalProfitPerTrade"] < 0].sum()
    totalProfit = df_resultsByTradeNum["totalProfitPerTrade"].sum()
    finalBalance = df_resultsByTradeNum["fundsAvailable"].iloc[0] + totalProfit
    percentReturns = finalBalance / df_resultsByTradeNum["fundsAvailable"].iloc[0] * 100
    
    df_resultsForStocks = pd.DataFrame({"stock": [stock],
                                        "numberOfTrades": [numberOfTrades],
                                        "totalDaysTraded": [totalDaysTraded],
                                        "numberOfWinningTrades": [numberOfWinningTrades],
                                        "numberOfLosingTrades": [numberOfLosingTrades],
                                        "winPercentage": [winPercentage],
                                        "profitFromWinners": [profitFromWinners],
                                        "lossesFromLosers": [lossesFromLosers],
                                        "totalProfit": [totalProfit],
                                        "finalBalance": [finalBalance],
                                        "percentReturns": [percentReturns]})
    return df_resultsForStocks

#%% Create buy sell table for single stock

def buySellTableSingleStock(df_resultsByTradeNum, stock):
    # Add Stock
    df_resultsByTradeNum["stock"] = stock
    
    # Create buy and sell dfs and then merge
    df_buy = df_resultsByTradeNum[["stock", "buyDate", "tradeNumber", "buyPrice", "stopLoss", "profitTarget"]]
    df_sell = df_resultsByTradeNum[["stock", "sellDate", "tradeNumber", "sellPrice", "stopLoss", "profitTarget"]]
    
    # Add buy and sell action
    df_buy["action"] = "buy"
    df_sell["action"] = "sell"
    
    # Rename columns
    df_buy = df_buy.rename(columns={"buyDate": "date", "buyPrice": "price"})
    df_sell = df_sell.rename(columns={"sellDate": "date", "sellPrice": "price"})
    
    # Concatenate buy and sell and sort buy date
    df_action = pd.concat([df_buy, df_sell])
    
    # Remove sells with NaT
    df_action = df_action[~df_action["date"].isna()]
    return df_action

#%% Create Buy Sell Table for all stocks

def buySellTableAllStocks(listOfStockToTradeFile, start, end, shortMACD, longMACD, signalMACD, rewardRiskRatio, 
                          stopLossWhenInf, diamondHands):
    print("Create buy, sell table for all stocks")
    
    # Create a df for price table
    df_price = pd.DataFrame(columns=["date"])
    
    # Get S&P info for list of all tickers
    df_snp = pd.read_csv(listOfStockToTradeFile)
    df_snp.sort_values("Symbol")
    
    # Initialize Data Frames
    df_action = pd.DataFrame()
    df_resultsForStocks = pd.DataFrame()
    
    # Get results for each ticker
    for i in range(len(df_snp)):
        stock = df_snp["Symbol"].iloc[i]
        print(stock, ":", i, "out of", len(df_snp))
        
        # Skip stocks with wierd tickers
        if "/" in stock or "^" in stock:
            continue
        
        # Get results for this stock
        plotDataBool = False
        df, df_resultsByTradeNum = pridictBuySellWithMACD(start, end, stock, shortMACD, longMACD, 
                                                          signalMACD, rewardRiskRatio, stopLossWhenInf,
                                                          diamondHands, plotDataBool) 
        
        # Create a price table for testing sim2
        df_price_temp = df[["Date", "Adj Close"]]
        df_price_temp = df_price_temp.rename(columns={"Date": "date", "Adj Close": stock})
        df_price = pd.merge(df_price, df_price_temp, on="date", how="outer")
        
        # Continue if df is empty (ticker does not exist in yahoo finance) or no trades occured
        if len(df_resultsByTradeNum) == 0:
            continue
        
        # Create a Table that provides results for all stocks
        df_resultsForStocks_temp = resultsForStocks(df_resultsByTradeNum, stock)
        
        # Create buy sell action table
        df_action_temp = buySellTableSingleStock(df_resultsByTradeNum, stock)
        
        # Concatenatetables
        df_action = pd.concat([df_action, df_action_temp])
        df_resultsForStocks = pd.concat([df_resultsForStocks, df_resultsForStocks_temp])
        
    # Sort action table
    df_action = df_action.sort_values(["date", "action"]).reset_index(drop=True)
    return df_action, df_resultsForStocks, df_price

#%% Simulate Returns

def simulateReturnsApprox(df_action):
    print("Simulate Approximate Returns")
    
    # Initial Balance
    stock = ""
    date = pd.to_datetime(start)
    tradeNumber = 0
    price = 0
    stopLoss = 0
    profitTarget = 0
    action = "initial"
    df_init = pd.DataFrame({"stock": [stock],
                            "date": [date],
                            "tradeNumber": [tradeNumber],
                            "price": [price],
                            "stopLoss": [stopLoss],
                            "profitTarget": [profitTarget],
                            "action": [action]})
    
    # Concatenate init and action
    df_sim = pd.concat([df_init, df_action]).reset_index(drop=True)
    
    # Add columns
    df_sim["numberOfShares"] = 0
    df_sim["tradePrice"] = 0
    df_sim["totalPositions"] = 0
    df_sim["totalCash"] = 0
    df_sim["accountValue"] = 0
    
    # Make start balance 100k
    df_sim["totalCash"].iloc[0] = 100000
    df_sim["accountValue"].iloc[0] = 100000
    
    # Simulate trades
    for i in range(1, len(df_sim)):
        if df_sim["action"].iloc[i] == "buy":
            # Get amount of money for this trade
            fundsForTrade = min(diversification * df_sim["accountValue"].iloc[i-1], df_sim["totalCash"].iloc[i-1])
            
            # Get number of shares to buy
            df_sim["numberOfShares"].iloc[i] = fundsForTrade // df_sim["price"].iloc[i]
            
            # Get Price of Trade
            df_sim["tradePrice"].iloc[i] = df_sim["price"].iloc[i] * df_sim["numberOfShares"].iloc[i]
            
            # Get Portfolio Balance
            df_sim["totalPositions"].iloc[i] = df_sim["totalPositions"].iloc[i-1] + df_sim["tradePrice"].iloc[i]
            
            # Get Account Balance
            df_sim["totalCash"].iloc[i] = df_sim["totalCash"].iloc[i-1] - + df_sim["tradePrice"].iloc[i]
            
            # Get Total Balance
            df_sim["accountValue"].iloc[i] = df_sim["totalPositions"].iloc[i] + df_sim["totalCash"].iloc[i]
        else:
            # Get Number of Shares
            df_sim["numberOfShares"].iloc[i] = df_sim["numberOfShares"][(df_sim["action"] == "buy") &
                                                                        (df_sim["stock"] == df_sim["stock"].iloc[i]) &
                                                                        (df_sim["tradeNumber"] == df_sim["tradeNumber"].iloc[i])].iloc[0]
            
            # Get Price of Trade
            df_sim["tradePrice"].iloc[i] = df_sim["price"].iloc[i] * df_sim["numberOfShares"].iloc[i]
            
            # Get Portfolio Balance
            df_sim["totalPositions"].iloc[i] = df_sim["totalPositions"].iloc[i-1] - df_sim["tradePrice"][(df_sim["action"] == "buy") &
                                                                                                         (df_sim["stock"] == df_sim["stock"].iloc[i]) &
                                                                                                         (df_sim["tradeNumber"] == df_sim["tradeNumber"].iloc[i])].iloc[0]
            
            # Get Account Balance
            df_sim["totalCash"].iloc[i] = df_sim["totalCash"].iloc[i-1] + + df_sim["tradePrice"].iloc[i]
            
            # Get Total Balance
            df_sim["accountValue"].iloc[i] = df_sim["totalPositions"].iloc[i] + df_sim["totalCash"].iloc[i]
    return df_sim
    
#%% Main

# Start 
start_time = time.time()
print("\n--- Simulate Returns")

# Get df_action table
df_action, df_resultsForStocks, df_price = buySellTableAllStocks(listOfStockToTradeFile, start, end, shortMACD, longMACD, 
                                                                  signalMACD, rewardRiskRatio, stopLossWhenInf, diamondHands)

# Get approximate sim values
df_simApprox = simulateReturnsApprox(df_action)

# Create basic action table for sim 2
df_action_simplified = df_simApprox[df_simApprox["action"] != "initial"]
df_action_simplified = df_action_simplified[["date", "stock", "numberOfShares", "action"]]

# Filter price down to start and stop time
df_price = df_price[(df_price["date"] >= pd.to_datetime(start)) & (df_price["date"] <= pd.to_datetime(end))]

# Write out action table and price table to csv
df_action_simplified.to_csv(output + r"\actionTable\actionTable.csv", index=False)
df_price.to_csv(output + r"\priceTable\priceTable.csv", index=False)

# Get exact sim values
df_buySell, df_simExact, df_rollup_year = simulateReturnsExact(actionTable, initialBalance, importCustomPriceTable, priceTable)

# Check for results directory
if not os.path.exists('../results'):
    os.makedirs('../results')
            
# Write out results
print("Write to excel")
with pd.ExcelWriter(output + r"\Results\Results_" + dt.now().strftime("%Y-%m-%d_%H-%M-%S") + ".xlsx") as writer:
    df_action.to_excel(writer, sheet_name="Action Table", index=False)
    df_resultsForStocks.to_excel(writer, sheet_name="Rollup by stock", index=False)
    df_buySell.to_excel(writer, sheet_name="Buy-Sell Matching", index=False)
    df_simApprox.to_excel(writer, sheet_name="Sim Approx", index=False)
    df_simExact.to_excel(writer, sheet_name="Sim Exact", index=False)
    df_rollup_year.to_excel(writer, sheet_name="Rollup By Year", index=False)

# Complete
print("\n--- Complete ---")
print("%s seconds" % (round(time.time() - start_time)))