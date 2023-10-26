# region imports
from AlgorithmImports import *
# endregion

class DancingOrangePanda(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2018, 1, 1)  # Set Start Date
        self.SetEndDate(2021, 1, 1)
        self.SetCash(100000)  # Set Strategy Cash
        self.qqq = self.AddEquity("QQQ", Resolution.Hour).Symbol

        self.entryTicket = None
        self.stopMarketTicket = None 
        self.entryTime = datetime.min
        self.stopMarketFillTime = datetime.min
        self.highestPrice = 0 

    def OnData(self, data: Slice):
        # wait 30 days since last stop market fill 
        if (self.Time - self.stopMarketFillTime).days < 30: 
            return 
        price = self.Securities[self.qqq].Price 
        # buy 90% of current buying power if you're not currently invested 
        if not self.Portfolio.Invested and not self.Transactions.GetOpenOrders(self.qqq):
            quantity = self.CalculateOrderQuantity(self.qqq, 0.9)
            self.entryTicket = self.LimitOrder(self.qqq, quantity, price, "Entry Order")
            self.entryTime = self.Time 

        # move limit price if not filled after one day
        if (self.Time - self.entryTime).days > 1 and self.entryTicket.Status != OrderStatus.Filled:
            self.entryTime = self.Time 
            updateFields = UpdateOrderFields()
            updateFields.LimitPrice = price
            self.entryTicket.Update(updateFields)

        # move up trailing stop price
        if self.stopMarketTicket and self.Portfolio.Invested: 
            if price > self.highestPrice: 
                self.highestPrice = price 
                updateFields = UpdateOrderFields()
                updateFields.StopPrice = 0.95 * price 
                self.stopMarketTicket.Update(updateFields) 

    def OnOrderEvent(self, orderEvent): 
        # only care if either the limit order or stop market order has been filled 
        if orderEvent.Status != OrderStatus.Filled: 
            return 
        # if limit order has been filled...
        if self.entryTicket is not None and self.entryTicket.OrderId == orderEvent.OrderId: 
            # then create the stop market ticket to be 5% below the average fill price of the limit order 
            self.stopMarketTicket = self.StopMarketOrder(self.qqq, -self.entryTicket.Quantity, 
                                                            0.95*self.entryTicket.AverageFillPrice)
        # if the stop market order has been filled
        if self.stopMarketTicket is not None and self.stopMarketTicket.OrderId == orderEvent.OrderId: 
            self.stopMarketFillTime = self.Time 
            self.highestPrice = 0 

        

        

        
