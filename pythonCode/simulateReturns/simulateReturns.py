# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 10:05:42 2021

@author: hungd
"""

#%% Imports

import os
import pandas as pd
import datetime
from func_timeout import func_timeout, FunctionTimedOut
from datetime import datetime as dt
import yfinance as yf

#%% For testing

# actionPath = r'C:\Users\hungd\Desktop\MACD\MACD\pythonCode\results\actionTable\actionTable_example6.csv'
# initialBalance = 100000
# diversification = 0.03
# importCustomPriceTable = True
# pricePath = r'C:/Users/hungd/Desktop/MACD/MACD/pythonCode/results/priceTable/priceTable.csv'

#%% Suppress slicing warnings

pd.options.mode.chained_assignment = None  # default='warn'

#%% Create Results, price, and action folders if they do not exist

def createDirs():
    # Paths
    output = r"..\results"
    priceTablePath = output + r"\priceTable"
    simResultsPath = output + r"\simResults"
    
    # Results
    if not os.path.exists(output):
        os.makedirs(output)
        
    # Price
    if not os.path.exists(priceTablePath):
        os.makedirs(priceTablePath)
        
    # Sim Results
    if not os.path.exists(simResultsPath):
        os.makedirs(simResultsPath)
        
#%% Import Action Table

def importActionTable(actionPath):
    df_action = pd.read_csv(actionPath)
    df_action.sort_values(['date', 'action'])
    return df_action

#%% Get Stock Data

def getStockData(stock, start, end):
    print("Getting stock data")
    
    try:
        df = func_timeout(10, yf.download, args=(stock, start, end))
    except FunctionTimedOut:
        print("\n\tCould not load", stock, "from Yahoo Finanace")
        df = pd.DataFrame()
    except:
        print("\n\tCould not load", stock, "from Yahoo Finanace")
        df = pd.DataFrame()
        
    # Reset Index
    df = df.reset_index()
    df = df[["Date", "Adj Close"]]
    df = df.rename(columns={"Date": "date", "Adj Close": stock})
    return df

#%% Create Trade Number

def createTradeNumber(df_action):
    print("Creating trade numbers")
    df_action["date"] = df_action["date"].apply(lambda x: pd.to_datetime(x))
    df_action["tradeNumber"] = df_action.groupby(["stock", "action"])["date"].rank("dense", ascending=True)
    return df_action

#%% Merge Price

def mergePrice(df_action, df_price):
    df_action['price'] = 0
    for i in range(len(df_action)):
        # Define variables
        stock = df_action['stock'].iloc[i]
        date = df_action['date'].iloc[i]
        
        # Price
        df_action['price'].iloc[i] = df_price[stock][df_price['date'] == date].iloc[0]
        
    # Sort Columns
    if 'numberOfShares' in list(df_action.columns):
        df_action = df_action[['date', 'stock', 'tradeNumber', 'numberOfShares', 'price', 'action']]
    else:
        df_action = df_action[['date', 'stock', 'tradeNumber', 'price', 'action']]
    return df_action

#%% Check for empty price

def checkForEmptyPrice(df_action):
    # Get list of all stocks without price
    stocksWithoutPrice = list(set(list(df_action['stock'][df_action['price'].isna()])))
    
    # Return if all stocks have a price (nothing wrong)
    if len(stocksWithoutPrice) == 0:
        return df_action
    
    # Remove stocks that have no price
    print('These stocks have no price and will be removed:', stocksWithoutPrice)
    df_action = df_action[~df_action['stock'].isin(stocksWithoutPrice)]
    return df_action

#%% Simulate Returns

def simulateReturnsApprox(df_action, initialBalance, diversification):
    print("Simulate Approximate Returns")
    
    # Initial Balance
    stock = ""
    date = df_action['date'][df_action['date'] == df_action['date'].min()].iloc[0]
    tradeNumber = 0
    price = 0
    action = "initial"
    df_init = pd.DataFrame({"stock": [stock],
                            "date": [date],
                            "tradeNumber": [tradeNumber],
                            "price": [price],
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
    df_sim["totalCash"].iloc[0] = initialBalance
    df_sim["accountValue"].iloc[0] = initialBalance
    
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
            df_sim["totalCash"].iloc[i] = df_sim["totalCash"].iloc[i-1] + df_sim["tradePrice"].iloc[i]
            
            # Get Total Balance
            df_sim["accountValue"].iloc[i] = df_sim["totalPositions"].iloc[i] + df_sim["totalCash"].iloc[i]
            
    # Filter down rows and columns
    df_sim = df_sim[['date', 'stock', 'action', 'tradeNumber', 'price', 'numberOfShares', 'tradePrice', 'totalCash']]
    df_sim = df_sim.iloc[1:].reset_index(drop=True)
    return df_sim

#%% Create stocksTable containing adj closes prices for each day specified

def createPriceTable(df_action, importCustomPriceTable, pricePath):
    print("Creating Price Table")
    
    # From custom price table
    if importCustomPriceTable:
        df_price = pd.read_csv(pricePath)
        df_price["date"] = df_price["date"].apply(lambda x: pd.to_datetime(x))
        return df_price
        
    # Define start and stop times
    start = df_action["date"].min()
    end = df_action["date"].max()
    startStr = start.strftime("%Y-%m-%d")
    endStr = (end + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    df_price = pd.DataFrame(columns=["date"])
    stocks = list(df_action["stock"].drop_duplicates())
    stocks.sort()
    for i in range(len(stocks)):
        print("Loading", stocks[i], ":", i, "out of", len(stocks))
        df_price_temp = getStockData(stocks[i], startStr, endStr)
        df_price = pd.merge(df_price, df_price_temp, how="outer", on="date")
        
    # Filter down price Table by start and stop times
    df_price = df_price[(df_price["date"] >= start) & (df_price["date"] <= end)]
    return df_price
  
#%% Calculate total cash
  
def calculateTotalCash(df_action, df_price, initialBalance):
    print("Calculating total cash")
    
    df_action["tradePrice"] = 0
    df_action["totalCash"] = 0
    
    # First Row
    date = df_action["date"].iloc[0]
    stock = df_action["stock"].iloc[0]
    numberOfShares = df_action["numberOfShares"].iloc[0]
    tradePrice = numberOfShares * df_price[stock][df_price["date"] == date].iloc[0]
    
    df_action["tradePrice"].iloc[0] = tradePrice
    df_action["totalCash"].iloc[0] = initialBalance - tradePrice
    
    # All other rows
    for i in range(1, len(df_action)):
        date = df_action["date"].iloc[i]
        stock = df_action["stock"].iloc[i]
        numberOfShares = df_action["numberOfShares"].iloc[i]
        tradePrice = numberOfShares * df_price[stock][df_price["date"] == date].iloc[0]
        action = df_action["action"].iloc[i]
        
        # Buy
        if action == "buy":
            df_action["tradePrice"].iloc[i] = tradePrice
            df_action["totalCash"].iloc[i] = df_action["totalCash"].iloc[i-1] - tradePrice
        else:
            df_action["tradePrice"].iloc[i] = tradePrice
            df_action["totalCash"].iloc[i] = df_action["totalCash"].iloc[i-1] + tradePrice
    return df_action

#%% Match buys with sells

def matchBuysWithSells(df_action):
    print("Matching buys with sells")
    
    df_buy = df_action[df_action["action"] == "buy"]
    df_sell = df_action[df_action["action"] == "sell"]
    
    # Create combined
    df_buySell = pd.merge(df_buy, df_sell, 
                          how="outer", 
                          on=["stock", "numberOfShares", "tradeNumber"],
                          suffixes=["_buy", "_sell"])
    
    df_buySell = df_buySell[["tradeNumber", "stock", "numberOfShares", 
                             "date_buy", "tradePrice_buy", "totalCash_buy", 
                             "date_sell", "tradePrice_sell", "totalCash_sell"]]
    df_buySell = df_buySell.sort_values("date_buy").reset_index(drop=True)
    return df_buySell

#%% Create a positions table

def createPositionsTable(df_buySell, df_price):
    print("Creating Positions")
    
    # Copy price table
    df_positions = df_price.copy()
    
    # Set all stocks equal to 0
    df_positions.iloc[:, 1:] = 0
    
    # Put when positions are held
    for i in range(len(df_buySell)):
        buyDate = df_buySell["date_buy"].iloc[i]
        sellDate = (df_buySell["date_sell"].iloc[i] if df_buySell["date_sell"].iloc[i] is not pd.NaT 
                    else df_price["date"].max() + datetime.timedelta(days=1))
        stock = df_buySell["stock"].iloc[i]
        numberOfShares = df_buySell["numberOfShares"].iloc[i]
        df_positions[stock][(df_positions["date"] >= buyDate) & (df_positions["date"] < sellDate)] = numberOfShares

    # Get positoins data
    df_positions.iloc[:, 1:] = df_positions.iloc[:, 1:] * df_price.iloc[:, 1:]
    return df_positions

#%% Merge action and positions table

def mergeActionPosition(df_action, df_positions):
    print("Merging actions and postions")
    
    # Get total cash at the end of the day
    df_action_daily = df_action.groupby("date").tail(1)
    df_action_daily = df_action_daily[["date", "totalCash"]]
    
    # Round total price and total cash
    df_action["tradePrice"] = df_action["tradePrice"].apply(lambda x: round(x, 2))
    df_action["totalCash"] = df_action["totalCash"].apply(lambda x: round(x, 2))
    
    # Log all daily activity into a list
    action = df_action.groupby("date")["action"].apply(lambda x: list(x))
    stock = df_action.groupby("date")["stock"].apply(lambda x: list(x))
    numberOfShares = df_action.groupby("date")["numberOfShares"].apply(lambda x: list(x))
    tradePrice = df_action.groupby("date")["tradePrice"].apply(lambda x: list(x))
    totalCash = df_action.groupby("date")["totalCash"].apply(lambda x: list(x))
    
    # Zip lists
    dailyActivity = list(zip(action, stock, numberOfShares, tradePrice, totalCash))
    for i in range(len(dailyActivity)):
        dailyActivity[i] = list(zip(*dailyActivity[i]))
    
    # Insert Trade info
    df_action_daily.insert(loc=1, column="tradeInfo", value=dailyActivity)
    
    # Merge action and position
    df_sim = pd.merge(df_action_daily, df_positions, how="right", on="date")
    
    # Insert total positions
    stockIdxStart = list(df_sim.columns).index("totalCash") + 1
    df_sim.insert(loc=3, column="totalPositions", value=df_sim.iloc[:, stockIdxStart:].sum(axis=1))
    
    # Sort by date
    df_sim = df_sim.sort_values("date")
    
    # Fill missing data for totalCash
    df_sim["totalCash"] = df_sim["totalCash"].fillna(method="ffill")
    
    # Insert Account Value
    df_sim.insert(loc=4, column="accountValue", value=df_sim["totalCash"] + df_sim["totalPositions"])
    return df_sim
    
#%% Rollup up results by year

def rollupByYear(df_sim):
    print("Rollup by year")
    
    df_sim.insert(loc=0, column="year", value=df_sim["date"].dt.year)
    year = list(set(df_sim["year"]))
    year.sort()
    
    df_results = pd.DataFrame()
    for i in range(len(year)):
        # Define variables
        df_year = df_sim[df_sim["year"] == year[i]]
        startDate = df_year["date"].min()
        endDate = df_year["date"].max()
        startBalance = df_year["accountValue"][df_year["date"] == startDate].iloc[0]
        endBalance = df_year["accountValue"][df_year["date"] == endDate].iloc[-1]
        profit = endBalance - startBalance
        percentReturns = profit / startBalance * 100
        
        # Create df
        df_results_temp = pd.DataFrame({"year": [year[i]], 
                                        "startDate": [startDate],
                                        "endDate": [endDate],
                                        "startBalance": [startBalance],
                                        "endBalance": [endBalance],
                                        "profit": [profit],
                                        "percentReturns": [percentReturns]})
        
        # Concatenate Results
        df_results = pd.concat([df_results, df_results_temp])
        
    # Reset index
    df_results = df_results.reset_index(drop=True)
    
    # Create Benchmark Table
    df_benchmark = pd.DataFrame({"year": [i for i in range(2000, 2022)],
                                 "benchmarkReturns": [-10.14, -13.04, -23.37, 26.38, 8.99, 3.00, 13.62, 3.53, -38.49, 23.45, 
                                                      12.78, 0.00, 13.41, 29.60, 11.39, -0.73, 9.54, 19.42, -6.24, 28.88,
                                                      16.26, 22.33]})
    
    # Merge results with benchmark
    df_results = pd.merge(df_results, df_benchmark, how="left", on="year")
  
    return df_results
        
#%% Write out results

def writeResults(df_price, df_action, df_buySell, df_simExact, df_rollup_year):
    # Write Price Table
    df_price.to_csv(r"..\results\priceTable\priceTable.csv", index=False)
    
    # Write out results
    print("Write to excel")
    print("Price Table Exported to .../results/priceTable")
    print("Results Exported to .../results/simResults")
    with pd.ExcelWriter(r"..\results\simResults\Results_" + dt.now().strftime("%Y-%m-%d_%H-%M-%S") + ".xlsx") as writer:
        df_action.to_excel(writer, sheet_name="Action Table", index=False)
        df_buySell.to_excel(writer, sheet_name="Buy-Sell Matching", index=False)
        df_simExact.to_excel(writer, sheet_name="Simulated Results", index=False)
        df_rollup_year.to_excel(writer, sheet_name="Rollup By Year", index=False)
        
#%% Main

def simulateReturnsExact(actionPath, initialBalance, importCustomPriceTable, pricePath, diversification):
    print("\n--- Simulate Exact Returns ---\n")
    
    # Create dirs
    createDirs()
    
    # Import Action Table
    df_action = importActionTable(actionPath)
    
    # Rank trades stock, then buy/sell (Example: AAPL buy 1 -> AAPL sell 1)
    df_action = createTradeNumber(df_action)
        
    # Create price Table
    df_price = createPriceTable(df_action, importCustomPriceTable, pricePath)
    
    # Include price in action table
    df_action = mergePrice(df_action, df_price)
    
    # Remove any stocks without price
    df_action = checkForEmptyPrice(df_action)
    
    # Simulate Approximate to get number of shares to buy
    if 'numberOfShares' in list(df_action.columns):
        df_simApprox = calculateTotalCash(df_action, df_price, initialBalance)
    else:
        df_simApprox = simulateReturnsApprox(df_action, initialBalance, diversification)
    
    # Match buys with sells
    df_buySell = matchBuysWithSells(df_simApprox)
    
    # Get Postions for each stock
    df_positions = createPositionsTable(df_buySell, df_price)
    
    # Add postions to action table
    df_simExact = mergeActionPosition(df_simApprox, df_positions)
    
    # Rollup by year
    df_rollup_year = rollupByYear(df_simExact)
    
    # Write out results
    writeResults(df_price, df_action, df_buySell, df_simExact, df_rollup_year)
    print("Complete")
    return df_buySell, df_simExact, df_rollup_year

# df_buySell, df_simExact, df_rollup_year = simulateReturnsExact(actionPath, initialBalance, importCustomPriceTable, pricePath, diversification)