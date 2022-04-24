# -*- coding: utf-8 -*-
"""
Created on Fri Dec 17 16:31:15 2021

@author: hungd
"""

#%% Imports

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget

#%% Main

class Home(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('home.ui', self)