# region imports
from AlgorithmImports import *
# endregion

class FocusedFluorescentPinkBaboon(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2016, 1, 1)
        self.SetCash(100000) 
        self.spy = self.AddEquity("SPY", Resolution.Daily).Symbol
        print("hello")


    def OnData(self, data: Slice):
        if not self.Portfolio.Invested:
            self.SetHoldings("SPY", 0.33)
            self.SetHoldings("BND", 0.33)
            self.SetHoldings("AAPL", 0.33)