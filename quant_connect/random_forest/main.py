# region imports
from AlgorithmImports import *
# endregion

class FocusedFluorescentPinkBaboon(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2023, 6, 1)
        self.SetCash(5000) 
        self.spy = self.AddEquity("SPY", Resolution.Daily).Symbol

    def OnData(self, data: Slice):
        if not self.Portfolio.Invested:
            self.SetHoldings("SPY", 0.33)
            self.SetHoldings("BND", 0.33)
            self.SetHoldings("AAPL", 0.33)