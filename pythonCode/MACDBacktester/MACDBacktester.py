# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 07:57:03 2021

@author: hungd
"""

#%% Imports

from addPaths import addPaths
addPaths()
import os
import pandas as pd
from MACDTradingStrategy import pridictBuySellWithMACD

#%% For Testing

# import datetime
# from datetime import date
# listOfStockToTradeFile = r"C:\Users\hungd\Desktop\MACD\MACD\constituents\constituents_example2.csv"
# start = (date.today() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')  # start date (1 year ago)
# end = date.today().strftime('%Y-%m-%d')                                     # end date (today)
# shortMACD = 12  # Short EMA
# longMACD = 26  # Long EMA
# signalMACD = 9  # Signal
# rewardRiskRatio = 2.5  # risk: reward
# stopLossWhenInf = 0.95  # Percent of Adj closing price value at time of buy
# diamondHands = False  # If true, once profit target is exceed, don't sell until first close price < close price of prev day

#%% Suppress slicing warnings

pd.options.mode.chained_assignment = None  # default='warn'

#%% Create Results, price, and action folders if they do not exist

def createDirs():
    # Paths
    output = r"..\results"
    actionPath = output + r"\actionTable"
    priceTablePath = output + r"\priceTable"
    stockPerformancePath = output + r"\stockPerformance"
    
    # Results
    if not os.path.exists(output):
        os.makedirs(output)
        
    # Action
    if not os.path.exists(actionPath):
        os.makedirs(actionPath)
        
    # Price
    if not os.path.exists(priceTablePath):
        os.makedirs(priceTablePath)
        
    # Stock Performance
    if not os.path.exists(stockPerformancePath):
        os.makedirs(stockPerformancePath)
        
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
    df_snp = df_snp.sort_values("Symbol")
    
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
        
        # Continue if df is empty (ticker does not exist in yahoo finance) or no trades occured
        if len(df_resultsByTradeNum) == 0:
            print(stock, 'not included')
            continue
            
        # Create a price table for testing sim2
        df_price_temp = df[["Date", "Adj Close"]]
        df_price_temp = df_price_temp.rename(columns={"Date": "date", "Adj Close": stock})
        df_price = pd.merge(df_price, df_price_temp, on="date", how="outer")
        
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

#%% Write out results

def writeResults(df_action, df_resultsForStocks, df_price):
    # Write Action Table
    df_action.to_csv(r"..\results\actionTable\actionTable.csv", index=False)
    
    # Write Stock Performance
    df_resultsForStocks.to_excel(r"..\results\stockPerformance\stockPerformance.xlsx", index=False)
    
    # Write Price Table
    df_price.to_csv(r"..\results\priceTable\priceTable.csv", index=False)
    
#%% MACD Results

def MACDBacktester(listOfStockToTradeFile, start, end, shortMACD, longMACD, signalMACD, rewardRiskRatio, 
                stopLossWhenInf, diamondHands):
    # Create Directories
    createDirs()
    
    # Get action table and results for all stocks
    df_action, df_resultsForStocks, df_price = buySellTableAllStocks(listOfStockToTradeFile, start, end, shortMACD, 
                                                                     longMACD, signalMACD, rewardRiskRatio, 
                                                                     stopLossWhenInf, diamondHands)
    
    # Write out results
    writeResults(df_action, df_resultsForStocks, df_price)
   
    print('Action Table exported to .../results/actionTable')
    print('Price Table exported to .../results/priceTable')
    print('Stock Performance Table exported to .../results/stockPerformance')
    print('Complete\n')
    return df_action
    
#%% Main

# df_action = MACDBacktester(listOfStockToTradeFile, start, end, shortMACD, longMACD, signalMACD, rewardRiskRatio, 
#                             stopLossWhenInf, diamondHands)