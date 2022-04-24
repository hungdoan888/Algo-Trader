# -*- coding: utf-8 -*-
"""
Created on Fri Dec 24 06:51:59 2021

@author: hungd
"""

#%% Imports

import os
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QTableWidgetItem
from registry import loadFromRegistry
from registry import saveToRegistry
from fileDialog import fileDialogBox
from MACDBacktester import MACDBacktester
import datetime
from datetime import date

import pandas as pd

#%% Main
class MACDActionToday(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uiFile = os.path.join(os.environ['PARENTDIR'], 'MACDActionToday/MACDActionToday.ui')
        uic.loadUi(uiFile, self)
    
        # Set Line Edit Values from Registry
        self.initiateValues()
        
        # Connect Line Edits
        self.connectLineEdits()
        
        # Connect Buttons
        self.connectButtons()
        
    # Set Line Edit Values and create initial plots
    def initiateValues(self):
        # Get registry
        registry, _ = loadFromRegistry()
        
        # Populate line edit fields
        self.lineEdit_constituents.setText(registry.get('MACDbacktest.constituents', 'constituents_example.csv'))  # constituents
        self.lineEdit_shortEMA.setText(registry.get('MACDbacktest.shortEMA', '12'))                  # shortEMA
        self.lineEdit_longEMA.setText(registry.get('MACDbacktest.longEMA', '26'))                    # longEMA
        self.lineEdit_signalEMA.setText(registry.get('MACDbacktest.signalEMA', '9'))                 # signalEMA
        self.lineEdit_rrr.setText(registry.get('MACDbacktest.rrr', '2.5'))                           # risk/reward ratio
        self.lineEdit_stopLossPercent.setText(registry.get('MACDbacktest.stopLossPercent', '0.95'))  # stopLossPercent
        self.lineEdit_totalCash.setText(registry.get('MACDbacktest.totalCash', '10000'))             # total cash
        self.lineEdit_accountValue.setText(registry.get('MACDbacktest.accountValue', '100000'))      # account value
        self.lineEdit_diversification.setText(registry.get('MACDbacktest.diversification', '0.03'))  # diversification
        
    # Save line edits to registry every time it changes
    def connectLineEdits(self):
        # Line Edits
        self.lineEdit_constituents.textChanged.connect(lambda: saveToRegistry('MACDbacktest.constituents', self.lineEdit_constituents.text()))           # constituents                                     # end date
        self.lineEdit_shortEMA.textChanged.connect(lambda: saveToRegistry('MACDbacktest.shortEMA', self.lineEdit_shortEMA.text()))                       # shortEMA
        self.lineEdit_longEMA.textChanged.connect(lambda: saveToRegistry('MACDbacktest.longEMA', self.lineEdit_longEMA.text()))                          # longEMA
        self.lineEdit_signalEMA.textChanged.connect(lambda: saveToRegistry('MACDbacktest.signalEMA', self.lineEdit_signalEMA.text()))                    # signalEMA
        self.lineEdit_rrr.textChanged.connect(lambda: saveToRegistry('MACDbacktest.rrr', self.lineEdit_rrr.text()))                                      # Risk/Reward Ratio
        self.lineEdit_stopLossPercent.textChanged.connect(lambda: saveToRegistry('MACDbacktest.stopLossPercent', self.lineEdit_stopLossPercent.text()))  # stopLossPercent
        self.lineEdit_totalCash.textChanged.connect(lambda: saveToRegistry('MACDbacktest.totalCash', self.lineEdit_totalCash.text()))                    # totalCash
        self.lineEdit_accountValue.textChanged.connect(lambda: saveToRegistry('MACDbacktest.accountValue', self.lineEdit_accountValue.text()))           # accountValue
        self.lineEdit_diversification.textChanged.connect(lambda: saveToRegistry('MACDbacktest.diversification', self.lineEdit_diversification.text()))  # diversification
    
    # Def Buttons connected
    def connectButtons(self):
        self.pushButton_constituents.clicked.connect(self.selectFile)
        self.pushButton_exportResults.clicked.connect(self.exportResults)
        
    # Select Constituents File
    def selectFile(self):
        filepath = os.path.split(self.lineEdit_constituents.text())[0]
        filename = fileDialogBox(initialdir=filepath, title="Select constituents file", filetypes="*.csv")
        self.lineEdit_constituents.setText(filename)

    # Export Results
    def exportResults(self):
        # Define Variables
        constituents = self.lineEdit_constituents.text()                            # stocks
        start = (date.today() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')  # start date (1 year ago)
        end = date.today().strftime('%Y-%m-%d')                                     # end date (today)
        shortEMA = int(self.lineEdit_shortEMA.text())                               # shortEMA
        longEMA = int(self.lineEdit_longEMA.text())                                 # longEMA
        signalEMA = int(self.lineEdit_signalEMA.text())                             # signalEMA
        rrr = float(self.lineEdit_rrr.text())                                       # risk/reward ratio
        stopLossPercent = float(self.lineEdit_stopLossPercent.text())               # stopLossPercent
        diamondHands = False
        
        self.df_action = MACDBacktester(constituents, start, end, shortEMA, longEMA, signalEMA, rrr, stopLossPercent, 
                                        diamondHands)
        ### For Testing ###
        # self.df_action = pd.read_csv(r'C:\Users\hungd\Desktop\MACD\MACD\forTesting\actionTable.csv')
        # self.df_action['date'] = self.df_action['date'].apply(lambda x: pd.to_datetime(x))
        ###################
        
        self.createBuySellTables()   
        self.addShares()
        self.writeDfsToTables()

    # Create Buy Sell Tables
    def createBuySellTables(self):
        # Filter on today's date
        df = self.df_action[self.df_action['date'] == pd.to_datetime(date.today().strftime('%Y-%m-%d'))]
       
        ### For Testing ###
        # df = self.df_action[self.df_action['date'] == pd.to_datetime((date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d'))]
        ###################
        
        # Buy Table
        df_buy = df[df['action'] == 'buy'].reset_index(drop=True)
        df_sell = df[df['action'] == 'sell'].reset_index(drop=True)
        
        # Arrange Columns
        df_buy = df_buy[['stock', 'price', 'stopLoss', 'profitTarget']]
        df_sell = df_sell[['stock', 'price', 'stopLoss', 'profitTarget']]
        
        self.df_buy = df_buy
        self.df_sell = df_sell
        
    # Add Shares and Trade Price
    def addShares(self):
        df_buy = self.df_buy
        totalCash = float(self.lineEdit_totalCash.text())
        accountValue = float(self.lineEdit_accountValue.text())
        diversification = float(self.lineEdit_diversification.text())
        
        # Determine whether to use diversification or to just split the total cash evenly
        if diversification * accountValue * len(df_buy) > totalCash:
            maxFundsPerTrade = totalCash / len(df_buy)
        else:
            maxFundsPerTrade = diversification * accountValue
        
        # Add Shares and Trade Price to buy table
        df_buy['shares'] = 0
        df_buy['tradePrice'] = 0
        
        # Determine Number of shares and tradeprice for each stock
        for i in range(len(df_buy)):
            df_buy['shares'].iloc[i] = maxFundsPerTrade // df_buy['price'].iloc[i]
            
        # Determine trade price
        df_buy['tradePrice'] = df_buy['price'] * df_buy['shares']
        self.df_buy = df_buy
        
    def writeDfsToTables(self):
        df_buy = self.df_buy
        df_sell = self.df_sell   
        
        # Clear table
        self.tableWidget_buy.setRowCount(1)  # Bring down to only header row for buy
        self.tableWidget_sell.setRowCount(1)  # Bring down to only header row for buy
        
        # Set number of rows
        newRowCount = max(len(df_buy), len(df_sell), 20)  # At least 20 rows looks good
        self.tableWidget_buy.setRowCount(newRowCount)  
        self.tableWidget_sell.setRowCount(newRowCount)  
        
        # Round Values
        df_buy['price'] = df_buy['price'].round(decimals=2)
        df_buy['stopLoss'] = df_buy['stopLoss'].round(decimals=2)
        df_buy['profitTarget'] = df_buy['profitTarget'].round(decimals=2)
        df_buy['tradePrice'] = df_buy['tradePrice'].round(decimals=2)
        df_sell['price'] = df_sell['price'].round(decimals=2)
        df_sell['stopLoss'] = df_sell['stopLoss'].round(decimals=2)
        df_sell['profitTarget'] = df_sell['profitTarget'].round(decimals=2)
        
        # If df_buy is empty
        if len(df_buy) == 0:
            self.tableWidget_buy.setItem(1, 0, QTableWidgetItem('No Buys Today'))
          
        # If df_sell is empty
        if len(df_sell) == 0:
            self.tableWidget_sell.setItem(1, 0, QTableWidgetItem('No Sells Today'))
        
        # Fill values for buy table
        for i in range(df_buy.shape[0]):
            for j in range(df_buy.shape[1]):
                self.tableWidget_buy.setItem(i+1, j, QTableWidgetItem(str(df_buy.iloc[i,j])))
                
        # Fill values for sell table
        for i in range(df_sell.shape[0]):
            for j in range(df_sell.shape[1]):
                self.tableWidget_sell.setItem(i+1, j, QTableWidgetItem(str(df_sell.iloc[i,j])))
        
        

        