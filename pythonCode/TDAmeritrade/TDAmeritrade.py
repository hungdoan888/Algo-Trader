# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 15:33:10 2021

@author: hungd
"""

#%% Imports

import os
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from registry import loadFromRegistry
from registry import saveToRegistry
from fileDialog import fileDialogBox

#%% Main

class TDAmeritradePaths(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uiFile = os.path.join(os.environ['PARENTDIR'], 'TDAmeritrade/TDAmeritrade.ui')
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
        self.lineEdit_apikey.setText(registry.get('TDconnect.apikey', 'api key file path'))                       # apikey
        self.lineEdit_accountNumber.setText(registry.get('TDconnect.accountNumber', 'account number file path'))  # accountNumber
        self.lineEdit_chromeDriver.setText(registry.get('TDconnect.chromeDriver', 'chrome driver file path'))     # chromeDriver
        self.lineEdit_token.setText(registry.get('TDconnect.token', 'token file path'))                           # token
        
    # Save line edits to registry every time it changes
    def connectLineEdits(self):
        # Line Edits
        self.lineEdit_apikey.textChanged.connect(lambda: saveToRegistry('TDconnect.apikey', self.lineEdit_apikey.text()))                       # apikey
        self.lineEdit_accountNumber.textChanged.connect(lambda: saveToRegistry('TDconnect.accountNumber', self.lineEdit_accountNumber.text()))  # account Number
        self.lineEdit_chromeDriver.textChanged.connect(lambda: saveToRegistry('TDconnect.chromeDriver', self.lineEdit_chromeDriver.text()))     # chromeDriver
        self.lineEdit_token.textChanged.connect(lambda: saveToRegistry('TDconnect.token', self.lineEdit_token.text()))                          # token
        
    # Def Buttons connected
    def connectButtons(self):
        self.pushButton_apikey.clicked.connect(self.selectAPIKey)
        self.pushButton_accountNumber.clicked.connect(self.selectAccountNumber)
        self.pushButton_chromeDriver.clicked.connect(self.selectChromeDriver)
        self.pushButton_token.clicked.connect(self.selectToken)
        
    # Select apikey
    def selectAPIKey(self):
        filepath = os.path.split(self.lineEdit_apikey.text())[0]
        filename = fileDialogBox(initialdir=filepath, title="Select API Key File", filetypes="*.*")
        self.lineEdit_apikey.setText(filename)

    # Select accountNumber
    def selectAccountNumber(self):
        filepath = os.path.split(self.lineEdit_accountNumber.text())[0]
        filename = fileDialogBox(initialdir=filepath, title="Select Account Number File", filetypes="*.*")
        self.lineEdit_accountNumber.setText(filename)
        
    # Select chromeDriver
    def selectChromeDriver(self):
        filepath = os.path.split(self.lineEdit_chromeDriver.text())[0]
        filename = fileDialogBox(initialdir=filepath, title="Select Chrome Driver", filetypes="*.*")
        self.lineEdit_chromeDriver.setText(filename)
        
    # Select token
    def selectToken(self):
        filepath = os.path.split(self.lineEdit_token.text())[0]
        filename = fileDialogBox(initialdir=filepath, title="Select Token File", filetypes="*.*")
        self.lineEdit_token.setText(filename)
     