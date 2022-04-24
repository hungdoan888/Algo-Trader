# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 09:55:28 2021

@author: hungd
"""

#%% Imports

from MACD3 import simulateReturns

#%% Testing functions for optimization of parameters
        
# Determine best Diversification
def determineBestDiversification(listOfStockToTradeFile, start, end, shortMACD, longMACD, signalMACD, rewardRiskRatio, 
                                 stopLossWhenInf, diamondHands, plotDataBool):
    diversification = [.01, .02, .03, .04, .05]
    totalReturns = []
    for i in range(len(diversification)):
        df_sim = simulateReturns(listOfStockToTradeFile, start, end, shortMACD, longMACD, signalMACD, rewardRiskRatio,
                                 stopLossWhenInf, diversification[i], diamondHands)
        totalReturns.append([diversification[i], df_sim["totalBalance"].iloc[len(df_sim) - 1]])
    return totalReturns

# Determine best Risk to reward ratio
def determineBestRiskRewardRatio(listOfStockToTradeFile, start, end, shortMACD, longMACD, signalMACD, stopLossWhenInf, 
                                 diversification, diamondHands):
    rewardRiskRatio = [2.6, 2.7, 2.8, 2.9, 3.0]
    totalReturns = []
    for i in range(len(rewardRiskRatio)):
        df_sim, df_rollup_year, df_resultsForStocks = simulateReturns(listOfStockToTradeFile, start, end, shortMACD, 
                                                                      longMACD, signalMACD, rewardRiskRatio[i], 
                                                                      stopLossWhenInf, diversification, diamondHands)
        totalReturns.append([rewardRiskRatio[i], df_rollup_year["percentReturns"].mean()])
        print(totalReturns)
        
# Optimize Input Parameters
def optimizeInputParameters(listOfStockToTradeFile, start, end, shortMACD, longMACD, signalMACD):
    writeToExcel=False
    rewardRiskRatio = [2.5, 2.75, 3, 3.25, 3.5]
    stopLossWhenInf = [.9, .95, .99]
    diversification = [.03]
    diamondHands = [True]
    totalReturns = []
    for i in range(len(rewardRiskRatio)):
        for j in range(len(stopLossWhenInf)):
            for k in range(len(diversification)):
                for l in range(len(diamondHands)):
                    df_sim, df_rollup_year, df_resultsForStocks = simulateReturns(listOfStockToTradeFile, start, end, shortMACD, 
                                                                                  longMACD, signalMACD, rewardRiskRatio[i], 
                                                                                  stopLossWhenInf[j], diversification[k],
                                                                                  diamondHands[l], writeToExcel)
                    
                    totalReturns.append([rewardRiskRatio[i], stopLossWhenInf[j], diversification[k], diamondHands[l], 
                                         df_rollup_year["percentReturns"].mean()])
                    print("\n--- Returns ---")
                    print("Reward to Risk Ratio:", rewardRiskRatio[i])
                    print("Stop Loss When Inf:", stopLossWhenInf[j])
                    print("Diversification:", diversification[k])
                    print("Diamond Hands:", diamondHands[l])
                    print("Total Returns:", df_rollup_year["percentReturns"].mean(), "\n")
                    print(totalReturns)