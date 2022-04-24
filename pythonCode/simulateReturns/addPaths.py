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
    
    # Research
    sys.path.append('../research')
