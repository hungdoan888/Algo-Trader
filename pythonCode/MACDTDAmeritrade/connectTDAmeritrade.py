# -*- coding: utf-8 -*-
"""
Created on Sun Nov 28 13:26:39 2021

@author: hungd
"""

#%% Imports

import tda
from tda import auth, client
import pandas as pd

#%% For Testing

# apiKeyFileName = r"C:\Users\hungd\Desktop\MACD\authentication\tdAmeritradeAPIKey"  # API Key
# accountNumberFileName = r"C:\Users\hungd\Desktop\MACD\authentication\tdAmeritradeAccountNumber"  # Account Number
# chromeDriverFileName = r"C:\Users\hungd\Desktop\MACD\authentication\chromedriver"
# tokenFileName = r"C:\Users\hungd\Desktop\MACD\authentication\token"

# stock = "T"
# quantity = 1
# stopPrice = 20
# price = 30

#%% TD Ameritrade Class

class TDConnect:
    def __init__(self, apiKeyFileName, accountNumberFileName, chromeDriverFileName, tokenFileName):
        # File Paths
        self.apiKeyFilePath = apiKeyFileName
        self.accountNumberFilePath = accountNumberFileName
        self.chromeDriverFilePath = chromeDriverFileName
        self.token_path = tokenFileName
        self.redirect_uri = 'https://localhost'
        
        # API key and Account Number
        self.getAPIKey()
        self.getAccountNumber()
        
        # Connect to TD Ameritrade
        self.connectToTDAmeritrade()
        
    # Get API Key
    def getAPIKey(self):
        apiFile = open(self.apiKeyFilePath)
        myAPIKey = apiFile.read()
        apiFile.close()
        self.api_key = myAPIKey + '@AMER.OAUTHAP'
 
    # Get Account Number
    def getAccountNumber(self):
        accountFile = open(self.accountNumberFilePath)
        accountNumber = accountFile.read()
        accountFile.close()
        self.accountNumber = accountNumber

    # Connect to TD Ameritrade
    def connectToTDAmeritrade(self):
        try:
            c = auth.client_from_token_file(self.token_path, self.api_key)
        except FileNotFoundError:
            from selenium import webdriver
            with webdriver.Chrome(self.chromeDriverFilePath) as driver:
                c = auth.client_from_login_flow(
                    driver, self.api_key, self.redirect_uri, self.token_path)
        self.client = c

    # Get Cash Balance and Account Value
    def getCashBalanceAndAccountValue(self):
        accountInfo = self.client.get_account(self.accountNumber).json()
        cashBalance = accountInfo['securitiesAccount']['currentBalances']['cashBalance']
        accountValue = accountInfo['securitiesAccount']['initialBalances']['accountValue']
        return cashBalance, accountValue
    
    # Get Order Info
    def getOrderInfo(self):
        orderInfo = self.client.get_account(self.accountNumber, fields=client.Client.Account.Fields.ORDERS).json()
        return orderInfo
    
    # Get Positions
    def getPositions(self):
        df_pos = pd.DataFrame()
        
        # Get positions
        accountInfo = self.client.get_account(self.accountNumber, fields=client.Client.Account.Fields.POSITIONS).json()
        positions = accountInfo["securitiesAccount"]["positions"]
        
        # Add Entries to DF
        for i in range(len(positions)):
            df_pos_temp = pd.DataFrame(positions[i]).reset_index()
            df_pos_temp = df_pos_temp[df_pos_temp["index"] == "symbol"]
            df_pos = pd.concat([df_pos, df_pos_temp])
        
        df_pos = df_pos[["instrument", "longQuantity", "averagePrice", "marketValue"]]
        df_pos = df_pos.rename(columns={"instrument": "stock", "longQuantity": "quantity"})
        return df_pos

    # Generate market buy order form
    def marketBuy(self, stock, quantity):
        orderInfo = tda.orders.equities.equity_buy_market(stock, quantity)
        return orderInfo

    # Generate marketSell order form
    def marketSell(self, stock, quantity):
        orderInfo = tda.orders.equities.equity_sell_market(stock, quantity)
        return orderInfo
     
    # Generate sell stop market order form (Sell when stock reaches stop loss)
    def stopMarketSell(self, stock, quantity, stopPrice):
        orderInfo = tda.orders.equities.equity_sell_market(stock, quantity)
        orderInfo.set_stop_price(stopPrice)
        orderInfo.set_order_type(tda.orders.common.OrderType.STOP)
        orderInfo.set_duration(tda.orders.common.Duration.GOOD_TILL_CANCEL)
        return orderInfo
    
    # Generate sell limit order form (Sell when stock reaches profit target)
    def limitSell(self, stock, quantity, price):
        orderInfo = tda.orders.equities.equity_sell_limit(stock, quantity, price)
        orderInfo.set_duration(tda.orders.common.Duration.GOOD_TILL_CANCEL)
        return orderInfo
    
    # Build 'one order cancels the other' order form
    def oneCancelsOther(self, orderInfo1, orderInfo2):
        orderInfo = tda.orders.common.one_cancels_other(orderInfo1, orderInfo2)
        return orderInfo
        
    # First order triggers second order form
    def firstTriggersSecond(self, orderInfo1, orderInfo2):
        orderInfo = tda.orders.common.first_triggers_second(orderInfo1, orderInfo2)
        return orderInfo
    
    # Buy with stop loss and profit target order form
    def buyWithStopLossProfitTarget(self, stock, quantity, stopPrice, price):
        # Fill out order forms
        buyOrder = self.marketBuy(stock, quantity)
        stopMarketSellOrder = self.stopMarketSell(stock, quantity, stopPrice)
        limitSellOrder = self.limitSell(stock, quantity, price)
        
        # Stop market sell and limit sell should cancel eachother
        sellOrder = self.oneCancelsOther(stopMarketSellOrder, limitSellOrder)
        
        # Buy then sell Order form
        buySellOrder = self.firstTriggersSecond(buyOrder, sellOrder)
        return buySellOrder
    
    # Place Order
    def placeOrder(self, orderInfo):
        resp = self.client.place_order(self.accountNumber, orderInfo)
        return resp
    
#%% Main

# # Create TD Ameritrade client connection
# td = TDConnect(apiKeyFileName, accountNumberFileName, chromeDriverFileName, tokenFileName)
# buySellOrder = td.buyWithStopLossProfitTarget(stock, quantity, stopPrice, price)
# resp = td.placeOrder(buySellOrder)
# print('Closed:', resp.is_closed, ',', 'Error:', resp.is_error)

# # Account Info
# cashBalance, accountValue = td.getCashBalanceAndAccountValue()

# # Get Positions
# df_pos = td.getPositions()

# # Get Order Info
# orderInfo = td.getOrderInfo()

# buyInfo = td.marketBuy(stock, quantity)
# marketSell = td.marketSell(stock, quantity)
# stopMarketSell = td.stopMarketSell(stock, quantity, stopPrice)
# limitSell = td.limitSell(stock, quantity, price)
# sellInfo = td.oneCancelsOther(stopMarketSell, limitSell)
# buySell = tda.orders.common.first_triggers_second(buyInfo, sellInfo)

# # resp = td.placeOrder(buySell)












