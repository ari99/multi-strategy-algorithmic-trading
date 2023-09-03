

from AlgorithmImports import *

from frameworkAlgo.mainHolder import Main
from frameworkAlgo.ltm.taggedPortfolioTarget import TaggedPortfolioTarget
from frameworkAlgo.risk.riskUtils import RiskUtils
from frameworkAlgo.state.stateManager import StateManager
from frameworkAlgo.state.states import SymbolAlgoState
from frameworkAlgo.state.tagModule import Tag


class PercentProfitProtectRisk(RiskManagementModel):

    def __init__(self, tag: Tag, stateManager: StateManager, maxProfitPercent=0.05):
        ''' Initializes a new instance of the TrailingStopRiskManagementModel class
            Args:
                maximumDrawdownPercent: The maximum percentage drawdown allowed for algorithm
                                    portfolio compared with the highest unrealized profit,
                                    defaults to 5% drawdown'''
        super().__init__()
        self.maxProfitPercent = abs(maxProfitPercent)
        self.tag: Tag = tag
        self.stateManager: StateManager = stateManager

    def ManageRisk(self, algorithm: QCAlgorithm, targets: List[PortfolioTarget]):
        riskAdjustedTargets = list()

        for kvp in algorithm.Securities:
            symbol = kvp.Key
            security = kvp.Value

            # Remove if not invested
            if not security.Invested:
                continue

            symbolState: SymbolAlgoState = self.stateManager.getSymbolAlgoState(symbol, self.tag.algoKey)
            if not symbolState or not symbolState.isInvested: # in this case we are invested from a different algoKey
                continue

            positionSide = PositionSide.Long if security.Holdings.IsLong else PositionSide.Short
            price = security.Holdings.Price
            absoluteHoldingsValue = price * abs(symbolState.runningTotalQuantity)

            originalCost = self.stateManager.getSymbolAlgoState(symbol, self.tag.algoKey).mostRecentAbsoluteCost

            profitPercentLong = (absoluteHoldingsValue - originalCost) / originalCost
            profitPercentShort = (originalCost- absoluteHoldingsValue ) / originalCost

            # TODO I dont think this works for shorts
            if (positionSide == PositionSide.Long and profitPercentLong > self.maxProfitPercent):
                Main.log(" In Long percent proft protect with "
                                + " abosoluteHoldingsValue " + str(absoluteHoldingsValue)
                                + " originalCost " + str(originalCost) + " profitPercent " + str(profitPercentLong))

                self.tag.description = "Profit Percent Liquidate Long: " + str(profitPercentLong)
                riskAdjustedTargets.append(TaggedPortfolioTarget(self.tag, symbol,
                                                                 RiskUtils.liquidateSymbolAlgoQuantity(
                                                                     symbolState.symbol,
                                                                     symbolState.algoKey)
                                                                 ))
            elif (positionSide == PositionSide.Short and profitPercentShort > self.maxProfitPercent):
                Main.log(" In Short percent proft protect with "
                         + " abosoluteHoldingsValue " + str(absoluteHoldingsValue)
                         + " originalCost " + str(originalCost) + " profitPercent " + str(profitPercentShort))

                self.tag.description = "Profit Percent Liquidate Short: " + str(profitPercentShort)
                riskAdjustedTargets.append(TaggedPortfolioTarget(self.tag, symbol,
                                                                 RiskUtils.liquidateSymbolAlgoQuantity(
                                                                     symbolState.symbol,
                                                                     symbolState.algoKey)
                                                                 ))


        #some comment
        return riskAdjustedTargets

