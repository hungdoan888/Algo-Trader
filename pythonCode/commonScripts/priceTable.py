# -*- coding: utf-8 -*-

#%% Imports

import datetime
import pandas as pd
from func_timeout import func_timeout, FunctionTimedOut
import yfinance as yf

#%% For Testing

# listOfStockToTradeFile = r"C:\Users\hungd\Desktop\MACD\MACD\constituents\constituents_example2.csv"
# stock = 'SWK'
# start = '2020-12-30'
# end = '2021-12-30'

#%% Get Stock Data

def getStockData(stock, start, end):
    # Need to add one day to include actual end day
    endStr = (datetime.datetime.strptime(end, "%Y-%m-%d") + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    try:
        df = func_timeout(10, yf.download, args=(stock, start, endStr))
    except FunctionTimedOut:
        print("\n\tCould not load", stock, "from Yahoo Finanace")
        df = pd.DataFrame()
    except:
        print("\n\tCould not load", stock, "from Yahoo Finanace")
        df = pd.DataFrame()
                         
    # Reset Index
    df = df.reset_index()
    return df

#%% Create Price Table

def createPriceTable(listOfStockToTradeFile, start, end):
    print('Fetching stock data')
    # Get S&P info for list of all tickers
    df = pd.read_csv(listOfStockToTradeFile)
    df = df.sort_values("Symbol")
    
    # Drop stocks with / or ^
    df = df[~df['Symbol'].str.contains('\^')]
    df = df[~df['Symbol'].str.contains('/')]
    
    # Create list of stocks
    stocks = list(df['Symbol'])
    
    # Create a df for price table
    df_price = pd.DataFrame(columns=["Date"])
    df_price.columns = pd.MultiIndex.from_product([df_price.columns, ['']])
    increment = 50
    leftIdx = 0
    rightIdx = increment
    
    # Can only pull ~100 stocks from yfinance at a time
    while leftIdx < len(stocks):
        print("stocks:", leftIdx, "-", min(rightIdx-1, len(stocks)))
        # Create list of stocks cut by left and right index
        stocks_temp = stocks[leftIdx:rightIdx]
        
        # Get stocks data from yahoo finance
        df_price_temp = getStockData(stocks_temp, start, end)
        
        # Ensure price_temp is multiindexed
        if not isinstance(df_price_temp.columns, pd.MultiIndex):
            df_price_temp.columns = pd.MultiIndex.from_tuples((("Date", ""), 
                                                               ("Open", stocks_temp[0]),
                                                               ("High", stocks_temp[0]),
                                                               ("Low", stocks_temp[0]),
                                                               ("Close", stocks_temp[0]),
                                                               ("Adj Close", stocks_temp[0]),
                                                               ("Volume", stocks_temp[0])))

        # Merge temp with price table
        df_price = pd.merge(df_price, df_price_temp, on="Date", how="outer")
        
        leftIdx += increment
        rightIdx += increment
    return df_price

#%% Get stock data from price table

def getStockDataFromPriceTable(df_price, stock):
    # Get Date
    date = df_price.loc[:, df_price.columns.get_level_values(0).isin({'Date'})]
    date.columns = date.columns.droplevel(1)
    
    # Get Stock data
    df_stock = df_price.loc[:, df_price.columns.get_level_values(1).isin({stock})]
    df_stock.columns = df_stock.columns.droplevel(1)
    
    # Append date to stock data
    df = pd.concat([date, df_stock], axis=1)
    return df
           

        
        
        
        