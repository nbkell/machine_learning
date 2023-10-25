# region imports
from AlgorithmImports import *
# endregion

class AlertFluorescentPinkCow(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2018, 1, 1)  # Set Start Date
        self.SetEndDate(2021, 1, 1)
        self.SetCash(100000)  # Set Strategy Cash
        self.spy = self.AddEquity("SPY", Resolution.Minute).Symbol
        self.rollingWindow = RollingWindow[TradeBar](2)
        self.Consolidate(self.spy, Resolution.Daily, self.CustomBarHandler)
        self.Schedule.On(self.DateRules.EveryDay(self.spy), 
                        self.TimeRules.BeforeMarketClose(self.spy, 15), 
                        self.ExitPositions) 

    def OnData(self, data):
        if not self.rollingWindow.IsReady:
            return 
        if not (self.Time.hour == 9 and self.Time.minute == 31): 
            return 
        if data[self.spy].Open >= 1.01*self.rollingWindow[0].Close:   # enter short postion
            self.SetHoldings(self.spy, -1)
        elif data[self.spy].Open <= 0.99*self.rollingWindow[0].Close:  # enter long position
            self.SetHoldings(self.spy, 1)
        
    def CustomBarHandler(self, bar): 
        self.rollingWindow.Add(bar) 

    def ExitPositions(self): 
        self.Liquidate(self.spy) 
