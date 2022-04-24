# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 19:07:45 2021

@author: hungd
"""

import os
import sys

def addPaths():
    # Parent
    os.environ['PARENTDIR'] = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    
    # Common Scripts
    sys.path.append('../commonScripts')
    
    # TD Ameritrade Paths
    sys.path.append('../TDAmeritrade')
    
    # MACD TD Ameritrade
    sys.path.append('../MACDTDAmeritrade')
    
    # MACD Action Today
    sys.path.append('../MACDActionToday')
    
    # Research
    sys.path.append('../MACDResearch')
    
    # MACD Trading Strategy Backtester
    sys.path.append('../MACDBacktester')
    
    # Simulate Returns
    sys.path.append('../simulateReturns')
