# -*- coding: utf-8 -*-
"""
Created on Fri Dec 17 12:22:06 2021

@author: hungd
"""

#%% Imports 

import json
import os

#%% Create Results, price, and action folders if they do not exist

def createDirs():
    # Registry
    if not os.path.exists('../registry'):
        os.makedirs('../registry')
        
#%% Load From Registry

def loadFromRegistry(key = ''):
    try:
        with open('../registry/registry.txt') as json_file:
            registry = json.load(json_file)
    except:
        createDirs()
        registry = {}
        
    if key not in registry:
        registry[key] = ''
    return registry, registry[key]

#%% Save to registry

def saveToRegistry(key, value):
    registry, _ = loadFromRegistry(key)
    registry[key] = value
    with open('../registry/registry.txt', 'w') as outfile:
        json.dump(registry, outfile, indent=4)