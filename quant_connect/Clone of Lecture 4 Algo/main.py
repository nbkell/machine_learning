# region imports
from AlgorithmImports import *
import pandas as pd 
import numpy as np
from talib import RSI
from datetime import datetime as dt
from scipy.stats import spearmanr
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.pipeline import Pipeline
import tensorflow
import qiskit
# endregion

# algorithm is to sell if SPY sells or drops by 10% 
class CalmBlackPelican(QCAlgorithm):
    def Initialize(self):
        
        self.SetStartDate(2020, 1, 1)  # Set Start Date
        self.SetEndDate(2021, 1, 1)
        self.SetCash(100000)  # Set Strategy Cash
        spy = self.AddEquity("SPY", Resolution.Daily)
        spy.SetDataNormalizationMode(DataNormalizationMode.Raw) 
        self.spy = spy.Symbol
        self.SetBenchmark("SPY")
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage, AccountType.Margin)

        self.entryPrice = 0 
        self.period = timedelta(31)
        self.nextEntryTime = self.Time 
      

    def OnData(self, data: Slice):
        if not self.spy in data:
            return 
        price = data[self.spy].Close
        if not self.Portfolio.Invested: 
            if self.nextEntryTime <= self.Time: 
                self.MarketOrder(self.spy, int(self.Portfolio.Cash/price))
                self.Log("BUY SPY @" + str(price))
                self.entryPrice = price
        elif price >= 1.1* self.entryPrice or price <= 0.9*self.entryPrice:
            self.Liquidate()
            self.Log("SELL SPY @" + str(price)) 
            self.nextEntryTime = self.Time + self.period




