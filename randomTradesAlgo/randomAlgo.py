#region imports
from datetime import datetime

from AlgorithmImports import *
from AlgorithmImports import Globals
#endregion
import random
from typing import Callable
import json

from typing import List

from common.commonUtils import CommonUtils
from randomTradesAlgo.statTracker import StatTracker


class RandomAlgo:
    def __init__(self):
        self.main = None
        self.orderedTransactions = {}
        self.sliceDebugCount = 0
        self.addedSecuritys = []
        self.utils = None
        self.statTracker = None

    # Define an Initialize method.
    # This method is the entry point of your algorithm where you define a series of settings.
    # LEAN only calls this method one time, at the start of your algorithm.
    def Initialize(self, main: QCAlgorithm) -> None:
        self.main = main
        self.orderedTransactions = {}
        self.sliceDebugCount = 0
        self.addedSecuritys = []
        self.utils = CommonUtils(self.main)
        # Set start and end dates
        self.main.SetStartDate(2014, 1, 1)
        #self.main.SetEndDate(2014, 3, 1)
        self.main.SetEndDate(2015, 1, 1)
        # Set the starting cash balance to $100,000 USD
        self.main.SetCash(10000)
        # Add data for the S&P500 index ETF

        self.addEquitys()

        self.statTracker = StatTracker(self.main)
        self.main.Debug(" End of init -----------")


    def addEquitys(self):
        tickets= ["LVMHF","TCEHY","OTGLY"]
        for ticket in tickets:
                self.main.Debug("Adding security: " + str(ticket))
                sec: Security = self.main.AddSecurity(SecurityType.Equity, ticket, Resolution.Daily)
                self.addedSecuritys.append(sec)


    # This method receives all the data you subscribe to in discrete time slices.
    # It's where you make trading decisions.
    def OnData(self, slice: Slice) -> None:
        self.utils.debugSlice(slice)

        # timeStr = slice.Time.strftime(Transaction.historyDateFormat)
        shouldTakeAction = random.randint(1, 12)
        quantity = random.randint(20, 100)
        buyOrSell = random.randint(1,2)

        # Get all order tickets
        orderTickets = self.main.Transactions.GetOrderTickets()

        # Get open order tickets
        openOrderTickets = self.main.Transactions.GetOpenOrderTickets()

        isFilled: Callable[[OrderTicket], bool] = lambda orderTicket: (orderTicket.Status == OrderStatus.Filled)
        filledOrderTickets = self.main.Transactions.GetOrderTickets(isFilled)
        holdings: List[Symbol]  = [x.Key for x in self.main.Portfolio if x.Value.Invested]
        self.makeTrades(slice)
        self.statTracker.processSlice(slice)



    def makeTrades(self, slice: Slice):
        for symbol, trade_bar in slice.Bars.items():
            tradeBar: TradeBar = trade_bar
            self.main.Debug("Slice bar item------ " + str(tradeBar.EndTime))
            holding: SecurityHolding = self.main.Portfolio[symbol]
            invested: bool = holding.Invested
            currentQuantity: float = holding.Quantity
            self.main.Debug("Currently invested " + str(currentQuantity) + " in " + str(holding.Symbol))

            shouldTakeAction = random.randint(1, 15)
            quantity = random.randint(20, 40)
            buyOrSell = random.randint(1, 2)
            if shouldTakeAction in range(1,3):
                if buyOrSell == 1:  # buy
                    self.main.MarketOrder(symbol, quantity)
                    self.main.Debug("buying : " + str(symbol) + "  " +  str(quantity))
                else:  # sell
                    if currentQuantity > 0:
                        if currentQuantity - quantity > 0:
                            quantityToSell = quantity
                        else:
                            quantityToSell = currentQuantity
                        self.main.Debug("selling : " + str(symbol) + "  " + str(quantityToSell) )
                        self.main.MarketOrder(symbol, (quantityToSell * (-1)))
                    else:
                        self.main.Debug("not selling " + str(symbol) +" because currentQuantity : " + str(currentQuantity) )
            else:
                self.main.Debug("Not taking any action")


    def OnOrderEvent(self, OrderEvent):

        if OrderEvent.FillQuantity == 0:
            return

        fetched = self.main.Transactions.GetOrderById(OrderEvent.OrderId)

        self.main.Debug("{} was filled. Symbol: {}. Quantity: {}. Direction: {}"
                   .format(str(fetched.Type),
                           str(OrderEvent.Symbol),
                           str(OrderEvent.FillQuantity),
                           str(OrderEvent.Direction)))


    def OnEndOfAlgorithm(self) -> None:
        self.main.Debug("In OnEndofAlgorithm")
        self.statTracker.processEndPortfolio(self.main.Portfolio)
        currentDateAndTime = datetime.now()
        currentTime = currentDateAndTime.strftime("%M_%S")
        self.statTracker.writeStats(Globals.DataFolder + "/output/btstats" + str(currentTime)+".json")
