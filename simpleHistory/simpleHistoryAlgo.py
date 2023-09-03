#region imports
from datetime import datetime
from random import randint

from AlgorithmImports import *
from AlgorithmImports import Globals
#endregion
from common.commonUtils import CommonUtils
from randomTradesAlgo.statTracker import StatTracker
from .orderUtils import OrderUtils
from .simpleHistoryUtils import SimpleHistoryUtils
from simpleHistory.transaction import Transaction
# this will give an error, needs to be like above : from transaction import Transaction
from typing import List


class SimpleHistoryAlgo():

    def __init__(self):
        self.main = None
        self.orderedTransactions = {}
        self.orderUtils = None
        self.historyUtils = SimpleHistoryUtils()
        self.commonUtils = None
        self.sliceDebugCount = 0
        self.addedSecuritys = []
        self.transactions: List[Transaction] = []
        self.transactionsGroupedByDay: Dict[str, List[Transaction]] = {}
        self.statTracker: StatTracker = None

    # Define an Initialize method.
    # This method is the entry point of your algorithm where you define a series of settings.
    # LEAN only calls this method one time, at the start of your algorithm.
    def Initialize(self, main: QCAlgorithm) -> None:
        self.main = main
        self.orderedTransactions = {}
        self.orderUtils = OrderUtils(self.main)
        self.historyUtils = SimpleHistoryUtils()
        self.commonUtils = CommonUtils(self.main)
        self.sliceDebugCount = 0
        self.addedSecuritys = []
        # Set start and end dates
        self.main.SetStartDate(2014, 1, 1)
        #self.main.SetEndDate(2016, 1, 1)

        #self.main.SetStartDate(2018, 3, 1)
        self.main.SetEndDate(2022, 12, 8)
        # Set the starting cash balance to $100,000 USD
        self.main.SetCash(100000)

        self.transactions = Transaction.readTransactions(Globals.DataFolder + "/transactionsFiltered.csv")

        self.transactions = self.historyUtils.addSecurityIdToTransactions(self.transactions)
        self.transactionsGroupedByDay = Transaction.makeGroupTransactionsByDay(self.transactions)

        sec: Security = self.main.AddSecurity(SecurityType.Equity,
         "AMZN", Resolution.Daily, dataNormalizationMode=DataNormalizationMode.Raw)  # , Market.USA)

        self.main.Securities["AMZN"].SetDataNormalizationMode(DataNormalizationMode.Raw)
        # UNCOMMENT TO RUN ALL
        #self.addEquitys()


        self.statTracker = StatTracker(self.main)

        self.main.Debug(" END OF INIT -----------")

    def addEquitys(self) -> None:
        count = 0
        for transaction in self.transactions:
            count += 1
            #if count > 10:
            #    break

            securityId = transaction.securityId
            self.main.Debug("Adding security: " + str(securityId))
            sec: Security = self.main.AddEquity(securityId.ToString(),
                                                Resolution.Daily, dataNormalizationMode=DataNormalizationMode.Raw)
            #this was needed as well otherwise the data waasnt raw
            self.main.Securities[str(sec.Symbol.Value)].SetDataNormalizationMode(DataNormalizationMode.Raw)

            self.addedSecuritys.append(sec)



    # This method receives all the data you subscribe to in discrete time slices.
    # It's where you make trading decisions.
    def OnData(self, slice: Slice) -> None:
        for symbol, trade_bar in slice.Bars.items():
            tradeBar: TradeBar = trade_bar
            if str(tradeBar.Symbol) == "AMZN" and randint(1, 100) < -1 :
                self.main.Debug("Slice bar item------ " + str(tradeBar.EndTime) +
                            "\n\t  tradeBar.Symbol: " + str(tradeBar.Symbol)
                            +"\n\t  tradeBar.Price: " +  str(tradeBar.Price)
                            + "\n\t  tradeBar.Value: " + str(tradeBar.Value)
                            + "\n\t  tradeBar.Close: " + str(tradeBar.Close)
                                )
                holding: SecurityHolding = self.main.Portfolio[symbol]


        self.statTracker.processSlice(slice)

        timeStr = slice.Time.strftime(Transaction.historyDateFormat)

        if timeStr in self.transactionsGroupedByDay:

            transactions: List[Transaction] = self.transactionsGroupedByDay[timeStr]
            self.main.Debug("Found transactions for this day " + timeStr)
            for transaction in transactions:
                securityId: SecurityIdentifier = transaction.securityId
                quantity = transaction.quantity
                date = transaction.date
                action = transaction.action
                if transaction.id not in self.orderedTransactions:
                    if slice.ContainsKey(securityId.Symbol):
                        self.main.Debug(" SLICE date "+ timeStr + " Making market order for: " + transaction.__str__() )
                        ticket: OrderTicket = self.main.MarketOrder(securityId.ToString(), quantity)
                        self.orderedTransactions[transaction.id] = ticket
        else:
            pass
            #self.main.Debug("No transactions for this day" + timeStr)



    def OnEndOfAlgorithm(self) -> None:
        self.main.Debug("In end of algo")
        self.statTracker.processEndPortfolio(self.main.Portfolio)
        currentDateAndTime = datetime.now()
        currentTime = currentDateAndTime.strftime("%M_%S")
        self.statTracker.writeStats(Globals.DataFolder + "/output/btstats" + str(currentTime)+".json")



    def OnOrderEvent(self, orderEvent: OrderEvent) -> None:

        if orderEvent.FillQuantity == 0:
            return

        fetched = self.main.Transactions.GetOrderById(orderEvent.OrderId)

        self.main.Debug("{} was filled. Symbol: {}. Quantity: {}. Direction: {}"
                   .format(str(fetched.Type),
                           str(orderEvent.Symbol),
                           str(orderEvent.FillQuantity),
                           str(orderEvent.Direction)))

