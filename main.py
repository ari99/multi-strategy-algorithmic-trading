# region imports

from AlgorithmImports import *
# from historyAlgo.historyAlgo import HistoryAlgo
from crossoverAlgo.crossoverAlgo import CrossoverAlgo
from frameworkAlgo.mainHolder import Main
from frameworkAlgo.myFramework import MyFramework
from frameworkAlgo.genericFrameworkAlgo import GenericFrameworkAlgorithm
from randomTradesAlgo.statTracker import StatTracker
from randomTradesAlgo.randomAlgo import RandomAlgo
from simpleHistory.simpleHistoryAlgo import SimpleHistoryAlgo
from datetime import datetime
# endregion


class DancingMagentaCamel(QCAlgorithm):
    """
    This is the main class which runs the trading algorithm. Uncomment an algorithm below to run it.
    """

    # algo: HistoryAlgo = HistoryAlgo()
    # algo: SimpleHistoryAlgo = SimpleHistoryAlgo()
    # algo: RandomAlgo = RandomAlgo()
    #algo: CrossoverAlgo = CrossoverAlgo()
    #algo = GenericFrameworkAlgorithm()
    algo: MyFramework = MyFramework()

    def Initialize(self):
        Main.setMain(self)
        self.algo.Initialize(self)
        self.statTracker = StatTracker(self)

    def OnData(self, slice: Slice):
        self.algo.OnData(slice)
        self.statTracker.processSlice(slice)

    # https://www.quantconnect.com/docs/v2/writing-algorithms/key-concepts/algorithm-engine?ref=v1
    def OnOrderEvent(self, orderEvent: OrderEvent):
        self.algo.OnOrderEvent(orderEvent)

    def OnSecuritiesChanged(self, changes: SecurityChanges) -> None:
        self.algo.OnSecuritiesChanged(changes)

    def OnEndOfAlgorithm(self) -> None:
        self.algo.OnEndOfAlgorithm()
        self.statTracker.processEndPortfolio(self.Portfolio)
        currentDateAndTime = datetime.now()
        currentTime = currentDateAndTime.strftime("%M_%S")
        self.statTracker.writeStats(Globals.DataFolder + "/output/btstats" + str(currentTime)+".json")



