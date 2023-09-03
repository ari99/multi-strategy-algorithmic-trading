import math

from AlgorithmImports import *

from typing import List

from frameworkAlgo.mainHolder import Main
from frameworkAlgo.ltm.taggedInsight import TaggedInsight
from frameworkAlgo.ltm.taggedPortfolioTarget import TaggedPortfolioTarget
from frameworkAlgo.state.keys import AlgoKey
from frameworkAlgo.state.stateManager import StateManager
from frameworkAlgo.state.states import SymbolAlgoState


# https://www.quantconnect.com/docs/v2/writing-algorithms/algorithm-framework/portfolio-construction/key-concepts
# https://github.com/QuantConnect/Lean/blob/master/Algorithm.Framework/Portfolio/EqualWeightingPortfolioConstructionModel.py
class PercentPortfolioConstruction(PortfolioConstructionModel):

    def __init__(self, main: QCAlgorithm, stateManager: StateManager):
        super().__init__()
        self.main = main
        self.stateManager: StateManager = stateManager

    def CreateTargets(self, algorithm: QCAlgorithm, insights: List[TaggedInsight]) -> List[PortfolioTarget]:
        targets = []
        percents = self.DetermineTargetPercent(insights)
        insight: TaggedInsight
        for insight in percents:

            # using Percent automatically converts percentage decimal to actualy quantity, use it with MarketOrder
            if insight is not None:
                portfolioTarget: TaggedPortfolioTarget = self.createPortfolioTarget(algorithm, insight, percents[insight])
                # this will keep the percentage as the quantity
                # portfolioTarget: TaggedPortfolioTarget = PortfolioTarget(insight.Symbol, percents[insight])
                if portfolioTarget is None:
                    Main.log("portfolio target is none for " + str(insight.Symbol) +
                             " percent " + str(percents[insight]) + " tag " + insight.tag.toStr(), logLevel=3)
                if insight.tag is None:
                    Main.log("insight  TAG is none for " + str(insight.Symbol) +
                             " percent " + str(percents[insight]), logLevel=3)
                if portfolioTarget is not None:
                    portfolioTarget.tag = insight.tag
                    targets.append(portfolioTarget)
        return targets

    def createPortfolioTarget(self,  algorithm: QCAlgorithm, insight: TaggedInsight,
                              percent: float) -> TaggedPortfolioTarget:
        symbolAlgoState: SymbolAlgoState = self.stateManager.getSymbolAlgoStateOrDefault(insight.Symbol,
                                                                                         insight.tag.algoKey)
        currentQuantity = symbolAlgoState.runningTotalQuantity

        portfolioTarget: TaggedPortfolioTarget = PortfolioTarget.Percent(algorithm, insight.Symbol,
                                                                         percent)
        quantity: float = math.floor(portfolioTarget.Quantity)
        quantity = math.floor(quantity)
        if symbolAlgoState and symbolAlgoState.isInvested:
            if quantity > 0 and currentQuantity < 0:
                quantity = quantity + abs(currentQuantity)
            elif quantity < 0 and currentQuantity > 0:
                quantity = quantity + (-1 * currentQuantity)


        # cant set quantity, just creating a new one for using floor
        portfolioTarget: TaggedPortfolioTarget = PortfolioTarget(insight.Symbol,math.floor(quantity))
        return portfolioTarget


    def DetermineTargetPercent(self, activeInsights: List[TaggedInsight]) -> Dict[Insight, float]:
        '''Will determine the target percent for each insight'''
        result = {}

        activeInsights = sorted(activeInsights, key=lambda x: x.Weight if x.Weight else 0, reverse=True)
        percentReserved = 0
        for insight in activeInsights:
            # holding: SecurityHolding = self.main.Portfolio.get(insight.Symbol)
            algoKey: AlgoKey = insight.tag.algoKey
            symbolAlgoState: SymbolAlgoState = self.stateManager.getSymbolAlgoStateOrDefault(
                insight.Symbol, insight.tag.algoKey)

            self.debugSymbolState(symbolAlgoState, algoKey, insight)
            # If not in the middle of an order
            if symbolAlgoState.orderExecutedButNotFilled == False and (
                            # New entry
                            (symbolAlgoState.isInvested is False and
                             (self.stateManager.percentUsed
                              + (self.stateManager.percent + percentReserved) < 1)) or
                            (symbolAlgoState.isInvested and insight.Direction == InsightDirection.Flat) or
                            (symbolAlgoState.isLong and insight.Direction == InsightDirection.Down) or
                            (symbolAlgoState.isShort and insight.Direction == InsightDirection.Up)
            ):
                # above only allows switching positions , not adding to longs or adding to shorts
                positionPercent = self.stateManager.percent * insight.Direction
                result[insight] = positionPercent
                percentReserved += self.stateManager.percent
                self.debugSymbolDirection(insight, positionPercent)
            else:
                self.debugNoAction(symbolAlgoState, algoKey, insight, percentReserved)

        return result

    def debugNoAction(self, symbolState: SymbolAlgoState, algoKey: AlgoKey,
                      insight: TaggedInsight, percentReserved: float):

        Main.log(" percentPortfolio -taking no action for insight . symbol: "
                 + str(insight.Symbol) + " algokey: " + str(algoKey)
                 + "\n Percent used: " + str(self.stateManager.percentUsed)
                 + " percent reserved: " + str(percentReserved))
        # + " Currently hold position: " + str(insight.Symbol in self.positions)
        if symbolState is not None:
            Main.log("percentPortfolio - symbolState quantity " + str(symbolState.runningTotalQuantity)
                     + " absolute cost " + str(symbolState.mostRecentAbsoluteCost)
                     + " isLong " + str(symbolState.isLong)
                     + " isShort " + str(symbolState.isShort)
                     + " isInvested " + str(symbolState.isInvested))
        else:
            Main.log("percentPortfolio - symbolState is None")

    def debugSymbolState(self, symbolState: SymbolAlgoState, algoKey: AlgoKey, insight: TaggedInsight):
        if symbolState and symbolState.isInvested:
            Main.log(str(algoKey) + " Already invested in " + str(insight.Symbol)
                     + " symbolState.IsLong " + str(symbolState.isLong)
                     + " symbolState.IsShort " + str(symbolState.isShort)
                     + "  insight.Direction " + str(insight.Direction)
                     + "  symbolState.quantity " + str(symbolState.runningTotalQuantity)
                     # + "  value " + str(holding.HoldingsValue)
                     + " percent used " + str(self.stateManager.percentUsed))
        else:
            Main.log(str(algoKey) + " not invested in " + str(insight.Symbol)
                     + " percent used " + str(self.stateManager.percentUsed))

    def debugSymbolDirection(self, insight: TaggedInsight, positionPercent):
        if insight.Direction == InsightDirection.Flat:
            Main.log("percentPortfolio - LIQUIDATING " + str(insight.Symbol))
        else:
            if insight.Direction == InsightDirection.Up:
                Main.log("percentPortfolio - BUYING " + str(insight.Symbol)
                         + " " + str(positionPercent))
            elif insight.Direction == InsightDirection.Down:
                Main.log("percentPortfolio - SHORTING " + str(insight.Symbol)
                         + " " + str(positionPercent))

    def OnSecuritiesChanged(self, algorithm: QCAlgorithm, changes: SecurityChanges) -> None:
        # This is only called on change of universe, not for buys/sells
        # Security additions and removals are pushed here.
        # This can be used for setting up algorithm state.
        # changes.AddedSecurities:
        # changes.RemovedSecurities:
        for security in changes.AddedSecurities:
            holding: SecurityHolding = algorithm.Portfolio.get(security.Symbol)
            Main.log(" security added  " + str(security.Symbol) + "  " + str(holding.Quantity))

        for security in changes.RemovedSecurities:
            holding: SecurityHolding = algorithm.Portfolio.get(security.Symbol)
            Main.log(" security REMOVED  " + str(security.Symbol) + "  " + str(holding.Quantity))

        super().OnSecuritiesChanged(algorithm, changes)

    def OnOrderEvent(self, orderEvent: OrderEvent) -> None:
        # no logic. percent maintained in StateManager
        pass

    '''
    def OnOrderEvent(self, orderEvent: OrderEvent) -> None:
        order = self.main.Transactions.GetOrderById(orderEvent.OrderId)

        if orderEvent.Status == OrderStatus.Filled:
            #self.main.Debug("===============Order Filled Event===================")
            #self.main.Debug(f"{self.main.Time}: {order.Type}: {orderEvent}")
            symbol = orderEvent.Symbol
            holding: SecurityHolding =  self.main.Portfolio.get(symbol)
            if holding.Invested:
                self.main.Debug("incrementing percent used  " + str(self.stateManager.percentUsed)
                                + " by " + str(self.stateManager.percent))
                self.stateManager.percentUsed += self.stateManager.percent
            else:
                self.main.Debug("decrementing percent used  " + str(self.stateManager.percentUsed) +
                                " by " + str(self.stateManager.percent))
                self.positions.pop(symbol)
                self.stateManager.percentUsed -= self.stateManager.percent
    '''




