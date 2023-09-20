# region imports
from AlgorithmImports import * 
import numpy as np
import pandas as pd
import pandas_datareader.data as web

# from pyfinance.ols import PandasRollingOLS
# replaces pyfinance.ols.PandasRollingOLS (no longer maintained)
from statsmodels.regression.rolling import RollingOLS
import statsmodels.api as sm
from talib import RSI, BBANDS, MACD, NATR, ATR

from sklearn.feature_selection import mutual_info_classif, mutual_info_regression

import matplotlib.pyplot as plt
import seaborn as sns
from AlgorithmImports import * 
import rf_training 

TRAIN_YEARS = 10
# endregion

class RandomForestAlgo(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2020, 1, 1)
        self.SetCash(5000)  
    
        # train initial model
        self.training = True
        self.CreateModel()
        self.training = False

    def CreateModel(self): 
        self.AddUniverse(self.TrainingFilter)
        self.training_syms = [] 
        #for sym in self.training_syms:
            # self.Debug(str(sym)) 
        self.train_df = self.History(self.training_syms, 360*TRAIN_YEARS, Resolution.Daily)

    def OnSecuritiesChanged(self, changes):
        if not self.training:
            return
        for security in changes.AddedSecurities:
            self.training_syms.append(security.Symbol)

    def TrainingFilter(self, coarse): 
        dvSort = sorted(coarse, key=lambda x : x.DollarVolume, reverse=True)
        ret = [x.Symbol for x in dvSort if x.Price > 10 and x.HasFundamentalData]
        return ret[:200]
                                 
    def OnData(self, data: Slice):
        for sym in self.training_syms:
            self.Debug(str(sym))