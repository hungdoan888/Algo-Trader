# -*- coding: utf-8 -*-
"""
Created on Sun Dec 26 19:20:41 2021

@author: hungd
"""

#%% Imports

import os
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from registry import loadFromRegistry
from registry import saveToRegistry
from fileDialog import fileDialogBox
from simulateReturns import simulateReturnsExact

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

import pandas as pd
import datetime
from func_timeout import func_timeout, FunctionTimedOut
import yfinance as yf

#%% Plot Options

matplotlib.rcParams['axes.facecolor'] = (27/256, 29/256, 35/256)
matplotlib.rcParams['figure.facecolor'] = (27/256, 29/256, 35/256)
matplotlib.rcParams['axes.edgecolor'] = 'white'
matplotlib.rcParams['xtick.color'] = 'white'
matplotlib.rcParams['ytick.color'] = 'white'
matplotlib.rcParams['text.color'] = 'white'
matplotlib.rcParams['figure.subplot.left'] = .07
matplotlib.rcParams['figure.subplot.bottom'] = .1
matplotlib.rcParams['figure.subplot.top'] = .9
matplotlib.rcParams['figure.subplot.right'] = .97
matplotlib.rcParams['axes.xmargin'] = 0
matplotlib.rcParams['axes.linewidth'] = .5
matplotlib.rcParams['grid.linewidth'] = .5
matplotlib.rcParams['grid.alpha'] = .5  # transparency
matplotlib.rcParams['font.size'] = 10

#%% Main

class simulateReturnsGUI(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uiFile = os.path.join(os.environ['PARENTDIR'], 'simulateReturns/simulateReturnsGUI.ui')
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
        self.lineEdit_action.setText(registry.get('simulateReturns.action', 'actionTable_example.csv'))         # action
        self.lineEdit_balance.setText(registry.get('simulateReturns.balance', '100000'))                        # balance date
        self.lineEdit_diversification.setText(registry.get('simulateReturns.diversification', '0.03'))          # diversification date
        self.lineEdit_priceTable.setText(registry.get('simulateReturns.priceTable', 'priceTable_example.csv'))  # priceTable
        
    # Save line edits to registry every time it changes
    def connectLineEdits(self):
        # Line Edits
        self.lineEdit_action.textChanged.connect(lambda: saveToRegistry('simulateReturns.action', self.lineEdit_action.text()))                             # action
        self.lineEdit_balance.textChanged.connect(lambda: saveToRegistry('simulateReturns.balance', self.lineEdit_balance.text()))                          # balance date
        self.lineEdit_diversification.textChanged.connect(lambda: saveToRegistry('simulateReturns.diversification', self.lineEdit_diversification.text()))  # diversification date
        self.lineEdit_priceTable.textChanged.connect(lambda: saveToRegistry('simulateReturns.priceTable', self.lineEdit_priceTable.text()))                 # priceTable
        
    # Def Buttons connected
    def connectButtons(self):
        self.pushButton_action.clicked.connect(self.selectActionTable)
        self.pushButton_priceTable.clicked.connect(self.selectPriceTable)
        self.pushButton_exportResults.clicked.connect(self.exportResults)
        
    # Select action table
    def selectActionTable(self):
        filepath = os.path.split(self.lineEdit_action.text())[0]
        filename = fileDialogBox(initialdir=filepath, title="Select Action Table", filetypes="*.csv")
        self.lineEdit_action.setText(filename)
        
    # Select price table
    def selectPriceTable(self):
        filepath = os.path.split(self.lineEdit_priceTable.text())[0]
        filename = fileDialogBox(initialdir=filepath, title="Select Price Table", filetypes="*.csv")
        self.lineEdit_priceTable.setText(filename)

    # Export Results
    def exportResults(self):
        actionPath = self.lineEdit_action.text()                       # stocks
        initialBalance = float(self.lineEdit_balance.text())           # balance date
        diversification = float(self.lineEdit_diversification.text())  # diversification date
        importCustomPriceTable = self.checkBox.isChecked()             # Custome Price Table
        pricePath = self.lineEdit_priceTable.text()                    # priceTable
        
        # Check for results directory
        _, self.df, _ = simulateReturnsExact(actionPath, initialBalance, importCustomPriceTable, pricePath, diversification)
        
        # Plot Returns
        self.plotReturns()
        
    # Plot Returns
    def plotReturns(self):
        # Define Variables
        date = self.df['date']
        accountValue = self.df['accountValue']
        
        # Get Spy Data
        self.getSPYData()
        date_spy = self.df_spy['Date']
        accountValue_spy = self.df_spy['accountValue']
        
        # Remove widget
        while self.stackedWidget.count() >= 1:
            self.stackedWidget.removeWidget(self.sc)
            
        # Create Plot
        self.sc = MplCanvas(self, width=5, height=2, dpi=100)
        self.sc.axes.plot(date, accountValue, color = 'skyblue', linewidth = 1.5, label = 'Simulated Returns')
        self.sc.axes.plot(date_spy, accountValue_spy, color = 'lightpink', linewidth = 1.5, label = 'SPY')
        
        # Set Title and legends
        self.sc.axes.legend(loc = 'upper left')
        
        # Add widget
        self.stackedWidget.addWidget(self.sc)
        
    # Get SPY Data
    def getSPYData(self):
        # Define Variables
        stock = 'SPY'
        start = self.df['date'].min()
        end = self.df['date'].max() + datetime.timedelta(days=1)
        initialBalance = float(self.lineEdit_balance.text())
        
        try:
            df_spy = func_timeout(10, yf.download, args=(stock, start, end))
        except FunctionTimedOut:
            print("\n\tCould not load", stock, "from Yahoo Finanace")
            df_spy = pd.DataFrame()
        except:
            print("\n\tCould not load", stock, "from Yahoo Finanace")
            df_spy = pd.DataFrame()
        
        # Reset Index
        df_spy = df_spy.reset_index()
        
        # Use only date and adj close price
        df_spy = df_spy[['Date', 'Adj Close']]
        
        # Calculate Account Value
        df_spy['numberOfShares'] = initialBalance // df_spy['Adj Close'].iloc[0]
        df_spy['cash'] = initialBalance - df_spy['numberOfShares'].iloc[0] * df_spy['Adj Close'].iloc[0]
        df_spy['totalPositions'] = df_spy['numberOfShares'] * df_spy['Adj Close']
        df_spy['accountValue'] = df_spy['totalPositions'] + df_spy['cash']
        self.df_spy = df_spy
        
#%% Plot

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)