# region imports
from AlgorithmImports import *
from collections import deque
# endregion

class RetrospectiveOrangeHyena(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2020, 1 ,1)  # Set Start Date
        self.SetEndDate(2021, 1, 1)
        self.SetCash(100000)  # Set Strategy Cash
        self.spy = self.AddEquity("SPY", Resolution.Daily).Symbol
        self.sma = CustomSimpleMovingAverage("SMA Indicator", 30)
        self.RegisterIndicator(self.spy, self.sma, Resolution.Daily) 
        self.yearly_low = self.MIN(self.spy, 365, Resolution.Daily) 
        self.yearly_high = self.MAX(self.spy, 365, Resolution.Daily)

        # set up yearly low indicator
        low_prices = self.History(self.spy, timedelta(365), Resolution.Daily)['low']
        for (time, price) in low_prices.loc[self.spy].items(): 
            self.yearly_low.Update(time, price) 

        # set up yearly high indicator
        high_prices = self.History(self.spy, timedelta(365), Resolution.Daily)['high']
        for (time, price) in high_prices.loc[self.spy].items(): 
            self.yearly_high.Update(time, price) 

    def OnData(self, data: Slice):
        if not self.sma.IsReady: 
            return 
        low = self.yearly_low.Current.Value
        high = self.yearly_high.Current.Value 

        price = self.Securities[self.spy].Price
        if 1.05 * price >= high and self.sma.Current.Value < price: 
            if not self.Portfolio[self.spy].IsLong:
                self.SetHoldings(self.spy, 1)
                # indentical to: 
                # quantity = self.CalculateOrderQuantity(self.spy, 1)
                # self.MarketOrder(self.spy, quantity)

        elif 0.95 * price <= low and self.sma.Current.Value > price: 
            if not self.Portfolio[self.spy].IsShort:
                self.SetHoldings(self.spy, -1) 
                # indentical to: 
                #quantity = self.CalculateOrderQuantity(self.spy, 1)
                #self.MarketOrder(self.spy, -quantity)
        else:
            self.Liquidate()
        
        self.Plot("Benchmark", "52W-High", high)
        self.Plot("Benchmark", "52W-Low", low)
        self.Plot("Benchmark", "SMA", self.sma.Current.Value)

class CustomSimpleMovingAverage(PythonIndicator):
    def __init__(self, name, period):
        self.Name = name
        self.Time = datetime.min 
        self.Value = 0 
        self.total = 0 
        self.queue = deque(maxlen=period)

    def Update(self, input): 
        self.Time = input.EndTime
        remove_val = 0 
        if len(self.queue) == self.queue.maxlen: 
            remove_val = self.queue[-1] 
        self.queue.appendleft(input.Close)
        self.total = self.total + input.Close - remove_val
        self.Value = self.total/len(self.queue)
        return len(self.queue) == self.queue.maxlen 
    



    
        
        
        


            



        

        
        
            
