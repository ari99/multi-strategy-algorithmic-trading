import random

from AlgorithmImports import *

from frameworkAlgo.alphaUtils import AlphaUtils
from frameworkAlgo.mainHolder import Main
from frameworkAlgo.params import Params
from frameworkAlgo.securityChanger import SecurityChanger, IndicatorKey, SymbolData

from frameworkAlgo.ltm.ltmIndicatorCreator import LtmIndicatorCreator
from frameworkAlgo.ltm.taggedInsight import TaggedInsight
from frameworkAlgo.state.keys import AlgoKey, SourceKey
from frameworkAlgo.state.stateManager import StateManager
from frameworkAlgo.state.states import SymbolAlgoState, CrossoverSymbolAlgoState
from frameworkAlgo.state.tagModule import Tag

'''
univers - 
    all nyse,nsdaq, amex
filter - 
    daily volume average greater than $50 mill 
    min price $5
setup
    close of spy is above 100 day sma
    close of 25 day sma is above close of 50 day sma
ranking
    highest rate of change over the last 200 trading days
entry 
    next open
stop loss
    below price of five times atr of last 20 days
reentry
    reenter next day if conditions apply
profit protections 
    trailing stop of 25 percenter
profity taking
    none
position sizing
    2 percent risk and 10 percent max percentage size with max of ten positions
'''
#https://github.com/QuantConnect/Lean/blob/master/Algorithm.Framework/Alphas/EmaCrossAlphaModel.py
class LtmAlpha(AlphaModel):

    def __init__(self,  main: QCAlgorithm, securityChanger: SecurityChanger, stateManager: StateManager):
        super().__init__()
        self.main = main
        self.alphaUtils = AlphaUtils(main)
        self.resolution = Resolution.Daily
        self.symbolStates: Dict[Symbol, CrossoverSymbolAlgoState] =  {}
        self.benchmarkPreviouslyBellowSma: bool = False
        self.benchmarkPreviouslyAboveSma: bool = False
        self.securityChanger = securityChanger
        self.stateManager = stateManager
        ind = LtmIndicatorCreator()
        self.fastPeriod = ind.fastPeriod
        self.slowPeriod = ind.slowPeriod
        self.benchmarkSmaPeriod = ind.benchmarkSmaPeriod
        self.algoKey = AlgoKey.LTM

        self.predictionInterval = Time.Multiply(Extensions.ToTimeSpan(self.resolution), self.fastPeriod)

        resolutionString = Extensions.GetEnumString(self.resolution, Resolution)
        self.Name = '{}({},{},{})'.format(self.__class__.__name__, self.fastPeriod, self.slowPeriod, resolutionString)


    def Update(self, algorithm: QCAlgorithm, slice: Slice) -> List[TaggedInsight]:
        # Updates this Alpha model with the latest data from the algorithm.
        # This is called each time the algorithm receives data for subscribed securities
        # Generate insights on the securities in the universe.
        doDebug = False

        r = random.randint(0, 60)
        if r == 2:
            doDebug = True

        insights: List[TaggedInsight] = []
        for symbol, symbolData in self.securityChanger.symbolDataBySymbol.items():
            fastIndicator = symbolData.indicators[IndicatorKey.FAST]
            slowIndicator = symbolData.indicators[IndicatorKey.SLOW]
            adxIndicator = symbolData.indicators[IndicatorKey.LTM_AVERAGE_DIRECTIONAL_INDEX]
            atrIndicator = symbolData.indicators[IndicatorKey.LTM_AVERAGE_TRUE_RANGE]
            benchmarkIndicator = symbolData.indicators[IndicatorKey.BENCHMARK_SMA]
            if symbol not in self.symbolStates:
                self.symbolStates[symbol] = CrossoverSymbolAlgoState(symbol)

            benchmark = Symbol.Create("SPY", SecurityType.Equity, Market.USA)
            algoUniverse = StateManager.getInstance().algoUniverses.get(self.algoKey)
            if fastIndicator.IsReady \
                    and slowIndicator.IsReady \
                    and benchmarkIndicator.IsReady \
                    and adxIndicator.IsReady \
                    and atrIndicator.IsReady \
                    and benchmark != symbol\
                    and symbol in algoUniverse:

                if doDebug:
                    Main.log(str(symbol) + "   " + str(slice.Time.date()))

                symbolAlgoState: SymbolAlgoState = self.stateManager.getSymbolAlgoState(symbol, AlgoKey.LTM)

                shortInsight: TaggedInsight = self.createShortInsight(symbolAlgoState,
                                            slowIndicator, fastIndicator,
                                            adxIndicator, symbol,
                                            symbolData,
                                            slice, doDebug)
                longInsight: TaggedInsight = self.createLongInsight(symbolAlgoState,
                                            slowIndicator, fastIndicator,
                                            adxIndicator, symbol,
                                            symbolData,
                                            slice, doDebug)

                if longInsight is not None and Params.LTM_LONGS:
                    insights.append(longInsight)
                elif shortInsight is not None and Params.LTM_SHORTS:
                    insights.append(shortInsight)

            else:
                if doDebug:
                    Main.log("At least One indicators not rdy")
                    Main.log(str(symbol) +
                    " fastIndicator " + str(fastIndicator.IsReady) +
                    " slowIndicator " + str(slowIndicator.IsReady) +
                    " benchmarkIndicator " + str(benchmarkIndicator.IsReady) +
                    " adxIndicator " + str(adxIndicator.IsReady) +
                    " atrIndicator "  + str(atrIndicator.IsReady))

            self.symbolStates[symbol].previouslyFastIsOverSlow = fastIndicator > slowIndicator
            self.symbolStates[symbol].previouslySlowIsOverFast = slowIndicator > fastIndicator
            self.benchmarkPreviouslyBellowSma = self.alphaUtils.isBenchmarkBellowSma(self.securityChanger)
            self.benchmarkPreviouslyAboveSma = self.alphaUtils.isBenchmarkAboveSma(self.securityChanger)


        return insights

    def createShortInsight(self, symbolAlgoState: SymbolAlgoState,
                           slowIndicator: IndicatorBase, fastIndicator: IndicatorBase,
                           adxIndicator, symbol: Symbol,
                           symbolData: SymbolData,
                           slice: Slice, doDebug: bool):
        benchmarkBellowSma = self.alphaUtils.isBenchmarkBellowSma(self.securityChanger)

        if symbolAlgoState == None or not symbolAlgoState.isInvested or symbolAlgoState.isLong:
            if slowIndicator > fastIndicator and benchmarkBellowSma \
                    and adxIndicator.Current.Value > 20:

                tag: Tag = Tag(AlgoKey.LTM, SourceKey.LTM_ALPHA, "Slow over fast short")
                Main.log("SENDING SHORT INSIGHT " + str(symbol) + " " + str(slice.Time), symbol=symbol)

                return TaggedInsight(tag, symbolData.symbol, self.predictionInterval,
                                  InsightType.Price, InsightDirection.Down, sourceModel="ltm", weight=1)
                # Insight.Price(symbolData.symbol, self.predictionInterval,
                #             InsightDirection.Down, sourceModel="ltm"))
            else:
                if doDebug:
                    Main.log(" slow> fast " + str(slowIndicator > fastIndicator) +
                             " isBenchmarkBellowSma "
                             + str(benchmarkBellowSma)
                             + "  ONE TRUE( previouslyFastIsOverSlow "
                             + str(self.symbolStates[symbol].previouslyFastIsOverSlow)
                             + "  benchmarkPreviouslyAboveSma  "
                             + str(self.benchmarkPreviouslyAboveSma)
                             + " )"
                             )
            return None
    def createLongInsight(self, symbolAlgoState: SymbolAlgoState,
                           slowIndicator: IndicatorBase, fastIndicator: IndicatorBase,
                           adxIndicator, symbol: Symbol,
                           symbolData: SymbolData,
                           slice: Slice, doDebug: bool) :
        benchmarkAboveSma = self.alphaUtils.isBenchmarkAboveSma(self.securityChanger)

        if symbolAlgoState == None or not symbolAlgoState.isInvested or symbolAlgoState.isShort:
            if fastIndicator > slowIndicator and benchmarkAboveSma \
                    and adxIndicator.Current.Value > 20:
                tag: Tag = Tag(AlgoKey.LTM, SourceKey.LTM_ALPHA, "Fast over slow buy")
                Main.log("SENDING BUY INSIGHT " + str(symbol) + " " + str(slice.Time), symbol=symbol)
                return TaggedInsight(tag, symbolData.symbol, self.predictionInterval,
                                  InsightType.Price, InsightDirection.Up, sourceModel="ltm", weight=1)
                # Insight.Price(symbolData.symbol, self.predictionInterval,
                #             InsightDirection.Up, sourceModel="ltm"))
            else:
                if doDebug:
                    Main.log(" fast>slow " + str(fastIndicator > slowIndicator)
                             + " isBenchmarkAboveSma "
                             + str(benchmarkAboveSma)
                             + " ONE TRUE(previouslyFastIsOverSlow "
                             + str(self.symbolStates[symbol].previouslySlowIsOverFast)
                             + " benchmarkPreviouslyBellowSma "
                             + str(self.benchmarkPreviouslyBellowSma) + " )"
                             )
            return None


    def OnSecuritiesChanged(self, algorithm: QCAlgorithm, changes: SecurityChanges) -> None:
        pass


