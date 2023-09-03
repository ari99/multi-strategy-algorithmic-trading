#region imports
from datetime import datetime
from AlgorithmImports import *
from AlgorithmImports import Globals
#endregion

from crossoverAlgo.crossoverDecider import CrossDecider, Signal
from crossoverAlgo.crossoverState import CrossState
from randomTradesAlgo.statTracker import StatTracker
from simpleHistory.transaction import Transaction
# this will give an error, needs to be like above : from transaction import Transaction
from typing import List

# this is based on https://www.quantconnect.com/forum/discussion/3275/sma-crossover-strategy/p1
#others:
# https://www.quantconnect.com/forum/discussion/1013/moving-average-cross-in-python/p1
# https://www.quantconnect.com/forum/discussion/9790/simple-moving-average-crossover-strategy-modified-with-volatility-testing-with-atr-but-win-and-loss-rates-are-0/p1
# https://www.quantconnect.com/forum/discussion/8309/moving-average-cross-in-python-with-stop-loss/p1


class CrossoverAlgo():

    def __init__(self):
        self.main = None
        self.statTracker: StatTracker = None
        self.transactions: List[Transaction] = []
        self.addedSecuritys = []
        self.sec: Equity = None
        self.symbol: Symbol = None
        self.faster: SimpleMovingAverage = None
        self.fast: SimpleMovingAverage = None
        self.slow: SimpleMovingAverage = None
        self.Tolerance = 0.00025
        self.crossState: CrossState = None
        self.crossDecider: CrossDecider = None

    # Define an Initialize method.
    # This method is the entry point of your algorithm where you define a series of settings.
    # LEAN only calls this method one time, at the start of your algorithm.
    def Initialize(self, main: QCAlgorithm) -> None:
        self.main = main
        # Set start and end dates
        #self.main.SetStartDate(1998, 1, 1)
        self.main.SetStartDate(2014, 1, 1)
        self.main.SetEndDate(2022, 12, 8)
        # Set the starting cash balance to $100,000 USD
        self.main.SetCash(100000)

        self.symbol = self.main.AddEquity("AMZN", Resolution.Daily,
                                          dataNormalizationMode=DataNormalizationMode.Raw).Symbol

        self.faster = self.main.SMA(self.symbol, 9, Resolution.Daily)
        self.fast = self.main.SMA(self.symbol, 40, Resolution.Daily)
        self.slow = self.main.SMA(self.symbol, 200, Resolution.Daily)
        self.crossState = CrossState(self.faster, self.fast, self.slow, self.main)
        self.crossDecider = CrossDecider(self.crossState, self.main)
        self.statTracker = StatTracker(self.main)

        self.crossState.previousDatetime = self.main.Time.min

        #https://www.quantconnect.com/forum/discussion/11688/best-way-to-liquidate-on-the-last-day-of-the-backtest/p1
        self.main.Schedule.On(self.main.DateRules.On(self.main.EndDate.year,
                                                     self.main.EndDate.month, self.main.EndDate.day),
                                                         self.main.TimeRules.At(0, 0),
                                                         self.LiquidateOnEnd)
        self.main.Debug(" End of init  -----------")

    def LiquidateOnEnd(self):
        self.main.Liquidate()
        self.main.Debug("liquidated on the last day")

    def addEquitys(self):
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
        month: int = slice.Time.date().month
        year: int = slice.Time.date().year
        day: int = slice.Time.date().day
        dateStr: str = str(month) + "-" + str(day) + "-" + str(year)
        self.handleSplits(slice)

        self.statTracker.processSlice(slice)

        if not self.slow.IsReady:
            return

        self.main.Debug(" previous action day " + str(self.crossState.previousActionDatetime))

        if self.crossState.isSameDayAsPreviousAction(slice.Time.date()):
            return

        self.crossState.symbol = self.symbol
        self.crossState.holdings = self.main.Portfolio[self.symbol].Quantity

        if(((month == 3 and day>=23) or (month == 4 and day<=3)) and year == 2020):
            self.main.Debug(str(month) + "-" + str(day) + "-" + str(year))
            shouldDebug = True
        else:
            shouldDebug = False

        self.__checkBuy(dateStr)
        self.__checkShort(dateStr)
        self.__checkLiquidate(dateStr)

        self.crossState.updateConsecutives()

    def __checkBuy(self, dateStr: str) -> None:
        buySignal: Signal = self.crossDecider.shouldBuy(False)

        if buySignal.shouldBuy:
            tagStr: str = "BUY: HOlDING<=0 AND "+buySignal.reason
            self.main.Debug(tagStr)
            self.crossState.previousAction = "buy"
            self.crossState.previousActionDatetime = slice.Time.date()
            self.main.Debug(dateStr + "  BUY  >> .4 price: "
                            + str(self.main.Securities[self.symbol].Price))
            self.main.SetHoldings(self.symbol, .4, tag=tagStr)

    def __checkShort(self, dateStr: str) -> None:
        shortSignal: Signal = self.crossDecider.shouldShort(False)
        if shortSignal.shouldShort:
            tagStr: str = "SHORT: HOLDING>=0 AND " + shortSignal.reason
            self.main.Debug(tagStr)
            self.crossState.previousAction = "short"
            self.crossState.previousActionDatetime = slice.Time.date()
            self.main.Debug(dateStr + "  SHORT  >> .4 price:"
                            + str(self.main.Securities[self.symbol].Price))
            self.main.SetHoldings(self.symbol, -.4, tag=tagStr)

    def __checkLiquidate(self, dateStr: str) -> None:
        liquidateSignal: Signal = self.crossDecider.shouldLiquidate()
        if liquidateSignal.shouldLiquidate:
            self.crossState.previousAction = "liquidate"
            self.crossState.previousActionDatetime = slice.Time.date()
            self.main.Debug(dateStr +
                            "  LIQUIDATE >> at " + str(self.main.Securities[self.symbol].Price) +
                            " because unrealized is "
                            + str(self.main.Portfolio[self.symbol].UnrealizedProfit))
            self.main.Liquidate(tag=liquidateSignal.reason)

    '''
    def getBuyReason(self):
        if self.crossState.isFastAboveSlowCrossover():
            return " Fast Above Slow "
        elif self.crossState.isFasterAboveSlowCrossover():
            return " Faster Above Slow "
        else:
            return " Unkown "

    def getShortReason(self):
        if self.crossState.isSlowAboveFastCrossover():
            return " Slow Above Fast "
        elif self.crossState.isSlowAboveFasterCrossover():
            return " Slow Above Faster "
        else:
            return " Unkown "
    '''

    def OnEndOfAlgorithm(self) -> None:
        self.main.Debug("---- In end of algo")
        self.main.Liquidate(tag="LIQUIDATE: END OF ALGO")
        self.statTracker.processEndPortfolio(self.main.Portfolio)
        currentDateAndTime = datetime.now()
        currentTime = currentDateAndTime.strftime("%M_%S")
        self.statTracker.writeStats(Globals.DataFolder + "/output/btstats" + str(currentTime)+".json")

    def OnOrderEvent(self, OrderEvent):

        if OrderEvent.FillQuantity == 0:
            return

        fetched = self.main.Transactions.GetOrderById(OrderEvent.OrderId)

        self.main.Debug("{} was filled. Symbol: {}. Quantity: {}. Direction: {}"
                   .format(str(OrderType(fetched.Type)),
                           str(OrderEvent.Symbol),
                           str(OrderEvent.FillQuantity),
                           str(OrderEvent.Direction)))

    def handleSplits(self, slice: Slice):
        month: int = slice.Time.date().month
        year: int = slice.Time.date().year
        day: int = slice.Time.date().day
        '''
        if slice.Time.date().year == 2022 and slice.Time.date().month == 6:
            self.main.Debug("======================")
            self.main.Debug(" month " + str(month))
            self.main.Debug(" day " + str(day))
        '''
        # https://www.quantconnect.com/datasets/quantconnect-us-equity-security-master/examples
        split = slice.Splits.get(self.symbol)
        if split:
            splitType = {0: "Warning", 1: "SplitOccurred"}.get(split.Type)
            self.main.Debug(
                f"{self.main.Time} >> SPLIT >> {splitType} - {split.Symbol} - {split.SplitFactor} - {self.main.Portfolio.Cash} - {self.main.Portfolio[self.symbol].Price}")
            # https://www.quantconnect.com/docs/v2/writing-algorithms/indicators/key-concepts#09-Reset-Indicators
            # https://www.quantconnect.com/docs/v2/writing-algorithms/indicators/manual-indicators#06-Warm-Up-Indicators
            self.slow.Reset()
            self.fast.Reset()
            self.faster.Reset()
            self.main.WarmUpIndicator(self.symbol, self.slow)
            self.main.WarmUpIndicator(self.symbol, self.fast)
            self.main.WarmUpIndicator(self.symbol, self.faster)
