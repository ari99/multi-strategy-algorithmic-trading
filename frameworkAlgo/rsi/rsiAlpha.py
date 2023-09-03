from AlgorithmImports import *

from frameworkAlgo.alphaUtils import AlphaUtils
from frameworkAlgo.mainHolder import Main
from frameworkAlgo.params import Params
from frameworkAlgo.securityChanger import SecurityChanger, IndicatorKey

from frameworkAlgo.ltm.taggedInsight import TaggedInsight
from frameworkAlgo.rsi.rsiIndicatorCreator import RsiIndicatorCreator
from frameworkAlgo.state.keys import AlgoKey, SourceKey
from frameworkAlgo.state.stateManager import StateManager
from frameworkAlgo.state.states import SymbolAlgoState
from frameworkAlgo.state.tagModule import Tag

#https://www.quantconnect.com/forum/discussion/3988/rsi-and-resistance-strategy/p1

'''

univers - 
    all nyse asdaq amex, want as many trades as possible
filter
    min price of $5
    average volumn greater than $25 mil
    average true price range percentage over last 10 days is three percent or more of the closing price of the stock- for volatility
setup
    3 day rsi is above 90
    last two days the close was higher than the previous
ranking
    highest seven day adx ( average directional index - trend indicator)
entry
    nex day, sell short 4 percent above previous closing price. limit order.
stop loss
    day after order, place a buy stop above the exectution price of three times ATR of the last ten days
reentry 
    reenter next day if conditions apply
profit protection
    none
profit taking
    if profit is 4% or higher  at close, get out next days close
    if after 2 days has not reached 4%, place a market order on close for the next day
position sizing
    2 percent risk
    and 10 percent size, a max of 10 positions
'''

# https://github.com/QuantConnect/Lean/blob/master/Algorithm.Framework/Alphas/RsiAlphaModel.py

class RsiAlpha(AlphaModel):
    #TODO entry is supposed to be a 7% limit
    numConsecutiveDays = 2
    def __init__(self,  main: QCAlgorithm,
                 securityChanger: SecurityChanger,
                 stateManager: StateManager):
        super().__init__()
        self.rsiPeriod = RsiIndicatorCreator().rsiPeriod

        self.main = main
        self.alphaUtils = AlphaUtils(main)
        self.resolution = Resolution.Daily
        self.securityChanger = securityChanger
        self.stateManager = stateManager
        self.predictionInterval = Time.Multiply(Extensions.ToTimeSpan(self.resolution), 1)
        self.algoKey = AlgoKey.RSI

    def Update(self, algorithm: QCAlgorithm, data: Slice) -> List[TaggedInsight]:

        insights = []
        benchmark = Symbol.Create("SPY", SecurityType.Equity, Market.USA)

        for symbol, symbolData in self.securityChanger.symbolDataBySymbol.items():

            symbolState: SymbolAlgoState = \
                self.stateManager.getSymbolAlgoStateOrDefault(symbol, AlgoKey.RSI)
            rsiIndicator = symbolData.indicators[IndicatorKey.RSI]
            atrIndicator = symbolData.indicators[IndicatorKey.RSI_ALPHA_AVERAGE_TRUE_RANGE]
            adxIndicator = symbolData.indicators[IndicatorKey.RSI_ALPHA_AVERAGE_DIRECTIONAL_INDEX]
            algoUniverse = StateManager.getInstance().algoUniverses.get(self.algoKey)

            if (rsiIndicator.IsReady
                and atrIndicator.IsReady
                and adxIndicator.IsReady
                and benchmark != symbol
                and symbol in algoUniverse):

                daysHigher = self.alphaUtils.daysHigherClose(symbol, self.numConsecutiveDays)

                if rsiIndicator.Current.Value > Params.RSI_SHORT_INDICATOR \
                        and daysHigher == True \
                        and not symbolState.isShort:
                    tag: Tag = Tag(AlgoKey.RSI, SourceKey.RSI_ALPHA, "RSI high - Short "+ str(rsiIndicator.Current.Value))
                    Main.log("Sending short Insight " + str(symbol)
                                    + " rsi value " + str(rsiIndicator.Current.Value) +
                                    " days higher " + str(daysHigher)
                                    + " is already short " + str(symbolState.isShort))
                    insights.append(
                        TaggedInsight(tag, symbolData.symbol, self.predictionInterval,
                                      InsightType.Price, InsightDirection.Down, sourceModel="rsi"))
                else:
                    pass
                    #algorithm.Debug("====NOT SHORTING " + str(symbol)
                    #                + " rsi value " + str(rsiIndicator.Current.Value)  +
                    #                " days higher " + str(daysHigher)
                    #                + " is already short " + str(symbolState.isShort))



                if rsiIndicator.Current.Value < Params.RSI_LONG_INDICATOR \
                        and self.alphaUtils.daysLowerClose(symbol, self.numConsecutiveDays) == True \
                        and not symbolState.isLong:
                    tag: Tag = Tag(AlgoKey.RSI, SourceKey.RSI_ALPHA, "RSI low - Long "+ str(rsiIndicator.Current.Value))
                    Main.log("Sending Buy Insight " + str(symbol))
                    insights.append(
                        TaggedInsight(tag, symbolData.symbol, self.predictionInterval,
                                      InsightType.Price, InsightDirection.Up, sourceModel="rsi"))



        return insights

    def OnSecuritiesChanged(self, algorithm: QCAlgorithm, changes: SecurityChanges) -> None:
        pass

