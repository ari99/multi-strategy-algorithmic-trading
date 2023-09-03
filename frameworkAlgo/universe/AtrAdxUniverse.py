
from AlgorithmImports import *
#from Selection.FundamentalUniverseSelectionModel import FundamentalUniverseSelectionModel

import random
from typing import List

from QuantConnect.Algorithm.Framework.Selection import FundamentalUniverseSelectionModel
from QuantConnect.Indicators import ExponentialMovingAverage, RateOfChange
from QuantConnect.Lean.Engine.DataFeeds import UniverseSelection

from frameworkAlgo.mainHolder import Main
from frameworkAlgo.params import Params
from frameworkAlgo.state.keys import AlgoKey
from frameworkAlgo.state.stateManager import StateManager
from frameworkAlgo.universe.AtrAdxUniverseSelectionData import AtrAdxUniverseSelectionData

'''univers - 
    all nyse,nsdaq, amex
filter - 
    daily volume average greater than $50 mill 
    min price $5
setup
    close of spy is above 100 day sma
    close of 25 day sma is above close of 50 day sma
ranking
    highest rate of change over the last 200 trading days'''

# original:
# https://github.com/QuantConnect/Lean/blob/62493f89868b18145d5eb3f9207f8136a1b885d2/Algorithm.Framework/Selection/EmaCrossUniverseSelectionModel.py

class CrossoverRocUniverse(CoarseFundamentalUniverseSelectionModel):
    '''Provides an implementation of FundamentalUniverseSelectionModel that subscribes to
    symbols with the larger delta by percentage between the two exponential moving average'''

    def __init__(self,
                 algoKey: AlgoKey,
                 adxPeriod = Params.ADX_RSI_UNIVERSE_PERIOD,
                 atrPeriod = Params.ATR_RSI_UNIVERSE_PERIOD,
                 universeCount = 20,
                 universeSettings = None):
        super().__init__(self.SelectCoarse, universeSettings)
        self.adxPeriod = adxPeriod
        self.atrPeriod = atrPeriod
        self.universeCount = universeCount
        self.atrMinPercent = .03
        # holds our coarse fundamental indicators by symbol
        self.symbolDatas = {}
        self.currentSymbols: List[Symbol] = []
        self.algoKey = algoKey

    def SelectCoarse(self, coarse: List[CoarseFundamental]) -> List[Symbol]:
        '''Defines the coarse fundamental selection function.
        Args:
            algorithm: The algorithm instance
            coarse: The coarse fundamental data used to perform filtering</param>
        Returns:
            An enumerable of symbols passing the filter'''

        fundementals: List[CoarseFundamental] = [c for c in coarse if c.HasFundamentalData]
        fundementals = list(filter(lambda cf: cf.DollarVolume >= 25000000, fundementals))
        fundementals = list(filter(lambda cf: cf.Price >= 5, fundementals))
        filtered: List[AtrAdxUniverseSelectionData] = []

        for cf in fundementals:
            if cf.Symbol not in self.averages:
                self.symbolDatas[cf.Symbol] = AtrAdxUniverseSelectionData(cf.Symbol, self.adxPeriod,
                                                                 self.atrPeriod)

            # grab the SelectionData instance for this symbol
            selectionData: AtrAdxUniverseSelectionData = self.symbolDatas.get(cf.Symbol)

            # Update returns true when the indicators are ready,
            #     average true price range percentage over last 10 days is three
            #     percent or more of the closing price of the stock- for volatility
            if selectionData.Update(cf.EndTime, cf.AdjustedPrice)\
                    and selectionData.atrPercent > .03 \
                    and cf.Symbol not in StateManager.getInstance().combinedUniverse:
                filtered.append(selectionData)


        filtered = sorted(filtered, key=lambda selectionData: selectionData.ADX, reverse = True)

        symbols: List[Symbol]= [x.Symbol for x in filtered[:self.universeCount]]

        bechmarkSymbol = Symbol.Create("SPY", SecurityType.Equity, Market.USA)
        symbols.append(bechmarkSymbol)
        self.currentSymbols = symbols
        StateManager.getInstance().addUniverse(self.algoKey, symbols)
        return symbols



    def debugFiltered(self,  filtered: List[UniverseSelection]) -> None:
        for selection in filtered:
            Main.log("symbol: " + str(selection.Symbol)+ " Roc: " + str(selection.RoC)
                           + " scaled Delta: " +  str(selection.ScaledDelta))


