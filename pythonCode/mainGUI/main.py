# -*- coding: utf-8 -*-
"""
Created on Mon Dec 13 21:23:36 2021

@author: hungd
"""

#%% imports

from addPaths import addPaths
addPaths()
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from home import Home
from TDAmeritrade import TDAmeritradePaths
from MACDTDAmeritrade import MACDTDAmeritrade
from MACDActionToday import MACDActionToday
from MACDResearch import MACDResearch
from MACDTradingStrategyBackTester import MACDTradingStrategyBackTester
from simulateReturnsGUI import simulateReturnsGUI

#%% Main

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        
        # Home Page
        self.comboBox.addItem('Home')
        self.home = Home()
        self.stackedWidget.addWidget(self.home)
        
        # TD Ameritrade
        self.comboBox.addItem('TD Ameritrade Paths')
        self.TDAmeritradePaths = TDAmeritradePaths()
        self.stackedWidget.addWidget(self.TDAmeritradePaths)
        
        # MACD TD Ameritrade
        self.comboBox.addItem('MACD TD Ameritrade Buy/Sell')
        self.MACDTDAmeritrade = MACDTDAmeritrade()
        self.stackedWidget.addWidget(self.MACDTDAmeritrade)
        
        # MACD Action Today
        self.comboBox.addItem('MACD Buy/Sell')
        self.MACDActionToday = MACDActionToday()
        self.stackedWidget.addWidget(self.MACDActionToday)
        
        # Research
        self.comboBox.addItem('MACD Research')
        self.MACDResearch = MACDResearch()
        self.stackedWidget.addWidget(self.MACDResearch)
        
        # MACD Trading Strategy
        self.comboBox.addItem('MACD Backtester')
        self.MACDTradingStrategyBackTester = MACDTradingStrategyBackTester()
        self.stackedWidget.addWidget(self.MACDTradingStrategyBackTester)
        
        # Returns Simulator
        self.comboBox.addItem('Returns Simulator')
        self.simulateReturnsGUI = simulateReturnsGUI()
        self.stackedWidget.addWidget(self.simulateReturnsGUI)
        
        # Connect Combo Box
        self.comboBox.currentIndexChanged.connect(self.comboBoxChanged)
        
    def comboBoxChanged(self):
        print('\n---', self.comboBox.currentText(), '---\n')
        self.stackedWidget.setCurrentIndex(self.comboBox.currentIndex())

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()