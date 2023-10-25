# region imports
from AlgorithmImports import *
# endregion

class CasualTanFrog(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2019, 1, 1)  # Set Start Date
        self.SetEndDate(2021, 1, 1)  # Set Start Date
        self.SetCash(100000)  # Set Strategy Cash
        self.rebalanceTime = datetime.min
        self.activeStocks = set()

        self.AddUniverse(self.CoarseFilter, self.FineFilter)
        self.UniverseSettings.Resolution = Resolution.Hour

        self.portfolioTargets = None 
    
    def CoarseFilter(self, coarse): 
        if self.Time <= self.rebalanceTime:
            return self.Universe.Unchanged
        self.rebalanceTime = self.Time + timedelta(30)
        dvSort = sorted(coarse, key=lambda x : x.DollarVolume, reverse=True)
        ret = [x.Symbol for x in dvSort if x.Price > 10 and x.HasFundamentalData]
        return ret[:200]
                                 
    def FineFilter(self, fine): 
        mcSort = sorted(fine, key= lambda x: x.MarketCap) 
        return [x.Symbol for x in mcSort if x.MarketCap > 0][:10]

    def OnSecuritiesChanged(self, changes): 
        for x in changes.RemovedSecurities:
            self.Liquidate(x.Symbol)
            self.activeStocks.remove(x.Symbol)
        for x in changes.AddedSecurities: 
            self.activeStocks.add(x.Symbol)
        m = len(self.activeStocks)
        self.portfolioTargets = [PortfolioTarget(x, 1/m) for x in self.activeStocks]

    def OnData(self, data: Slice):
        # check to see if active universe has changed
        if not self.portfolioTargets: 
            return 
        # make sure we have correct data on all active stocks we want to change
        for x in self.activeStocks: 
            if x not in data:
                return
        self.SetHoldings(self.portfolioTargets)
        self.portfolioTargets = None 

    
