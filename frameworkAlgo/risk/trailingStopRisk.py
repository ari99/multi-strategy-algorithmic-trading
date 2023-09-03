import datetime

from AlgorithmImports import *

from frameworkAlgo.common.positionChange import PositionChange
from frameworkAlgo.ltm.taggedPortfolioTarget import TaggedPortfolioTarget
from frameworkAlgo.risk.riskUtils import RiskUtils
from frameworkAlgo.state.keys import AlgoKey, SourceKey
from frameworkAlgo.state.stateManager import StateManager
from frameworkAlgo.state.states import SymbolAlgoState
from frameworkAlgo.state.tagModule import Tag


class HoldingsState:
    def __init__(self, entryDirection: PositionSide,
                 currentHoldingValue: float,
                 currentPrice: float,
                 currentDate: datetime
                 ):
        self.entryDirection = entryDirection
        self.entryDirectionStr = "long" if entryDirection==PositionSide.Long else "short"
        self.entryDate = currentDate
        self.entryPrice = currentHoldingValue

        self.maxAbsoluteHoldingsValue = currentHoldingValue
        self.maxPrice =  currentPrice
        self.dateOfMax: datetime = currentDate

        self.minAbsoluteHoldingsValue = currentHoldingValue
        self.minPrice =  currentPrice
        self.dateOfMin: datetime = currentDate

# https://github.com/QuantConnect/Lean/blob/master/Algorithm.Framework/Risk/TrailingStopRiskManagementModel.py
class MyTrailingStopRiskManagementModel(RiskManagementModel):

    '''Provides an implementation of IRiskManagementModel that limits the maximum possible loss
    measured from the highest unrealized profit'''
    def __init__(self, tag: Tag, stateManager: StateManager, maximumDrawdownPercent=0.25):
        '''Initializes a new instance of the TrailingStopRiskManagementModel class
        Args:
            maximumDrawdownPercent: The maximum percentage drawdown allowed for algorithm
             portfolio compared with the highest unrealized profit, defaults to 5% drawdown'''
        super().__init__()
        self.maximumDrawdownPercent = abs(maximumDrawdownPercent)
        self.trailingAbsoluteHoldingsState: Dict[Symbol, Dict[AlgoKey, HoldingsState]] = dict()
        self.algoKey: AlgoKey = tag.algoKey # dont really need if 1 instance per algo, but leaving for now as an extra check
        self.sourceKey: SourceKey = tag.sourceKey
        self.stateManager: StateManager = stateManager

    def updateMax(self, symbol: Symbol, currentHoldingsValue: float, previousState: HoldingsState,
                  price: float, time: datetime) -> None:
        if (currentHoldingsValue > previousState.maxAbsoluteHoldingsValue):
            previousState.maxPrice = price
            previousState.dateOfMax = time
            previousState.maxAbsoluteHoldingsValue = currentHoldingsValue

            self.trailingAbsoluteHoldingsState[symbol][self.algoKey] = previousState

    def updateMin(self, symbol: Symbol, currentHoldingsValue: float,
                  previousState: HoldingsState, price: float, time: datetime) -> None:
        if (currentHoldingsValue < previousState.minAbsoluteHoldingsValue):
            previousState.minPrice = price
            previousState.dateOfMin = time
            previousState.minAbsoluteHoldingsValue = currentHoldingsValue

            self.trailingAbsoluteHoldingsState[symbol][self.algoKey] = previousState

    def createTaggedMax(self, symbol: Symbol, drawdown: float,
                        currentHoldingsValue: float, price: float, time: datetime) -> TaggedPortfolioTarget:
        exitState: HoldingsState = self.trailingAbsoluteHoldingsState[symbol][self.algoKey]
        self.trailingAbsoluteHoldingsState[symbol].pop(self.algoKey, None)
        # liquidate
        description: str = ("Drawdown Risk Liquidate Long " +
                            " exitHoldingsValue " + str(currentHoldingsValue)
                            + " exitPrice " + str(price)
                            + " exitDate " + str(time)
                            + " drawdown " + str(drawdown)
                            + " maxHoldingsValue " + str(exitState.maxAbsoluteHoldingsValue)
                            + " dateOfMax " + str(exitState.dateOfMax)
                            + " maxPrice " + str(exitState.maxPrice)
                            + " entryDirection " + str(exitState.entryDirectionStr)
                            + " entryDate " + str(exitState.entryDate)
                            + " entryPrice " + str(exitState.entryPrice)
                            )
        tag: Tag = Tag(self.algoKey, self.sourceKey, description)
        pt = TaggedPortfolioTarget(tag, symbol, RiskUtils.liquidateSymbolAlgoQuantity(symbol,
                                            self.algoKey))

        return pt

    def createTaggedMin(self, symbol: Symbol, drawdown: float,
                        currentHoldingsValue: float, price: float, time: datetime) -> TaggedPortfolioTarget:
        exitState: HoldingsState = self.trailingAbsoluteHoldingsState[symbol][self.algoKey]
        self.trailingAbsoluteHoldingsState[symbol].pop(self.algoKey, None)
        # liquidate
        description: str = ("Drawdown Risk Liquidate Short " +
                            " exitHoldingsValue " + str(currentHoldingsValue)
                            + " exitPrice " + str(price)
                            + " exitDate " + str(time)
                            + " drawdown " + str(drawdown)
                            + " minHoldingsValue " + str(exitState.minAbsoluteHoldingsValue)
                            + " dateOfMin " + str(exitState.dateOfMin)
                            + " minPrice " + str(exitState.minPrice)
                            + " entryDirection " + str(exitState.entryDirectionStr)
                            + " entryDate " + str(exitState.entryDate)
                            + " entryPrice " + str(exitState.entryPrice)
                            )
        tag: Tag = Tag(self.algoKey, self.sourceKey, description)
        pt = TaggedPortfolioTarget(tag, symbol, RiskUtils.liquidateSymbolAlgoQuantity(symbol,
                                            self.algoKey))

        return pt

    def ManageRisk(self, algorithm: QCAlgorithm, targets: List[PortfolioTarget]):
        '''Manages the algorithm's risk at each time step
        Args:
            algorithm: The algorithm instance
            targets: The current portfolio targets to be assessed for risk'''
        riskAdjustedTargets = list()

        for kvp in algorithm.Securities:
            symbol = kvp.Key
            security = kvp.Value

            # Remove if not invested
            if not security.Invested:
                if symbol in self.trailingAbsoluteHoldingsState:
                    self.trailingAbsoluteHoldingsState.pop(symbol, None)
                continue

            symbolState: SymbolAlgoState = self.stateManager.getSymbolAlgoStateOrDefault(symbol, self.algoKey)
            if not symbolState or not symbolState.isInvested:  # in this case we are invested from a different algoKey
                if symbol in self.trailingAbsoluteHoldingsState \
                  and self.algoKey in self.trailingAbsoluteHoldingsState[symbol] :
                    self.trailingAbsoluteHoldingsState[symbol].pop(self.algoKey, None)
                continue

            position = PositionSide.Long if security.Holdings.IsLong else PositionSide.Short
            currentPositionStr = "long" if position == PositionSide.Long else "short"

            currentHoldingsValue = abs(symbolState.runningTotalQuantity * security.Price)
            currentState: HoldingsState = HoldingsState(position, currentHoldingsValue, security.Price, algorithm.Time)

            if symbol in self.trailingAbsoluteHoldingsState:
                    if self.algoKey not in self.trailingAbsoluteHoldingsState[symbol]:
                        self.trailingAbsoluteHoldingsState[symbol][self.algoKey] = currentState
            else:
                self.trailingAbsoluteHoldingsState[symbol] = {}
                self.trailingAbsoluteHoldingsState[symbol][self.algoKey] = currentState

            previousState = self.trailingAbsoluteHoldingsState[symbol][self.algoKey]

            # Check for new max (for long position) or min (for short position) absolute holdings value
            self.updateMax(symbol, currentHoldingsValue, previousState, security.Price, algorithm.Time)
            self.updateMin(symbol, currentHoldingsValue, previousState, security.Price, algorithm.Time)

            if currentHoldingsValue < previousState.maxAbsoluteHoldingsValue and position == PositionSide.Long:
                drawdown = abs((previousState.maxAbsoluteHoldingsValue - currentHoldingsValue) / previousState.maxAbsoluteHoldingsValue)

                if drawdown > self.maximumDrawdownPercent:
                    portfolioTarget: TaggedPortfolioTarget = \
                        self.createTaggedMax(symbol, drawdown, currentHoldingsValue, security.Price, algorithm.Time)
                    riskAdjustedTargets.append(portfolioTarget)

            if currentHoldingsValue > previousState.minAbsoluteHoldingsValue and position == PositionSide.Short:
                drawdown = abs((currentHoldingsValue - previousState.minAbsoluteHoldingsValue ) / previousState.minAbsoluteHoldingsValue)

                if drawdown > self.maximumDrawdownPercent:
                    portfolioTarget: TaggedPortfolioTarget = \
                        self.createTaggedMin(symbol, drawdown, currentHoldingsValue, security.Price, algorithm.Time)
                    riskAdjustedTargets.append(portfolioTarget)

        return riskAdjustedTargets

    def OnOrderEvent(self, orderEvent: OrderEvent, orderChange: PositionChange) -> None:
        symbol: Symbol = orderChange.symbol
        algoKey: AlgoKey = orderChange.algoKey
        if algoKey == self.algoKey or algoKey == algoKey.COMMON:
            if orderChange.isLiquidateSymbolAlgo or orderChange.isReversePositionSymbolAlgo:
                if symbol in self.trailingAbsoluteHoldingsState and self.algoKey in self.trailingAbsoluteHoldingsState[symbol]:
                    self.trailingAbsoluteHoldingsState[symbol].pop(self.algoKey, None)

            if orderChange.isLiquidateSymbolAlgo or orderChange.isReversePositionSymbol:
                if symbol in self.trailingAbsoluteHoldingsState:
                    self.trailingAbsoluteHoldingsState.pop(symbol, None)
