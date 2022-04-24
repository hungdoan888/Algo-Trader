# -*- coding: utf-8 -*-
"""
Created on Fri Dec 24 06:51:59 2021

@author: hungd
"""

#%% Imports

import os
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from registry import loadFromRegistry
from registry import saveToRegistry
from fileDialog import fileDialogBox
from MACDBacktester import MACDBacktester

#%% Main
class MACDTradingStrategyBackTester(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uiFile = os.path.join(os.environ['PARENTDIR'], 'MACDBacktester/MACDTradingStrategyBackTester.ui')
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
        self.lineEdit_start.setText(registry.get('MACDbacktest.start', '2020-01-01'))                # start date
        self.lineEdit_end.setText(registry.get('MACDbacktest.end', '2021-01-01'))                    # end date
        self.lineEdit_shortEMA.setText(registry.get('MACDbacktest.shortEMA', '12'))                  # shortEMA
        self.lineEdit_longEMA.setText(registry.get('MACDbacktest.longEMA', '26'))                    # longEMA
        self.lineEdit_signalEMA.setText(registry.get('MACDbacktest.signalEMA', '9'))                 # signalEMA
        self.lineEdit_rrr.setText(registry.get('MACDbacktest.rrr', '2.5'))                           # risk/reward ratio
        self.lineEdit_stopLossPercent.setText(registry.get('MACDbacktest.stopLossPercent', '0.95'))  # stopLossPercent
        
    # Save line edits to registry every time it changes
    def connectLineEdits(self):
        # Line Edits
        self.lineEdit_constituents.textChanged.connect(lambda: saveToRegistry('MACDbacktest.constituents', self.lineEdit_constituents.text()))           # constituents
        self.lineEdit_start.textChanged.connect(lambda: saveToRegistry('MACDbacktest.start', self.lineEdit_start.text()))                                # start date
        self.lineEdit_end.textChanged.connect(lambda: saveToRegistry('MACDbacktest.end', self.lineEdit_end.text()))                                      # end date
        self.lineEdit_shortEMA.textChanged.connect(lambda: saveToRegistry('MACDbacktest.shortEMA', self.lineEdit_shortEMA.text()))                       # shortEMA
        self.lineEdit_longEMA.textChanged.connect(lambda: saveToRegistry('MACDbacktest.longEMA', self.lineEdit_longEMA.text()))                          # longEMA
        self.lineEdit_signalEMA.textChanged.connect(lambda: saveToRegistry('MACDbacktest.signalEMA', self.lineEdit_signalEMA.text()))                    # signalEMA
        self.lineEdit_rrr.textChanged.connect(lambda: saveToRegistry('MACDbacktest.rrr', self.lineEdit_rrr.text()))                                      # Risk/Reward Ratio
        self.lineEdit_stopLossPercent.textChanged.connect(lambda: saveToRegistry('MACDbacktest.stopLossPercent', self.lineEdit_stopLossPercent.text()))  # stopLossPercent
    
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
        constituents = self.lineEdit_constituents.text()               # stocks
        start = self.lineEdit_start.text()                             # start date
        end = self.lineEdit_end.text()                                 # end date
        shortEMA = int(self.lineEdit_shortEMA.text())                  # shortEMA
        longEMA = int(self.lineEdit_longEMA.text())                    # longEMA
        signalEMA = int(self.lineEdit_signalEMA.text())                # signalEMA
        rrr = float(self.lineEdit_rrr.text())                          # risk/reward ratio
        stopLossPercent = float(self.lineEdit_stopLossPercent.text())  # stopLossPercent
        diamondHands = False
        
        # Check for results directory
        MACDBacktester(constituents, start, end, shortEMA, longEMA, signalEMA, rrr, 
                    stopLossPercent, diamondHands)