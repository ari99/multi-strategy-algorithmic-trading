from datetime import datetime, timedelta

from AlgorithmImports import *

from frameworkAlgo.mainHolder import Main
from frameworkAlgo.ltm.taggedPortfolioTarget import TaggedPortfolioTarget
from frameworkAlgo.risk.riskUtils import RiskUtils
from frameworkAlgo.state.stateManager import StateManager
from frameworkAlgo.state.states import SymbolAlgoState
from frameworkAlgo.state.tagModule import Tag


class MaxDaysRisk(RiskManagementModel):

    def __init__(self, tag: Tag, stateManager: StateManager, maxDays=3):
        '''
            Initializes a new instance of the TrailingStopRiskManagementModel class
            Args: maximumDrawdownPercent: The maximum percentage drawdown allowed for algorithm
                portfolio compared with the highest unrealized profit, defaults to 5% drawdown
        '''
        super().__init__()
        self.maxDays = abs(maxDays)
        self.tag: Tag = tag
        self.stateManager: StateManager = stateManager

    def ManageRisk(self, algorithm: QCAlgorithm, targets: List[PortfolioTarget]):
        riskAdjustedTargets = list()

        for kvp in algorithm.Securities:
            symbol = kvp.Key
            security = kvp.Value

            symbolState: SymbolAlgoState = self.stateManager.getSymbolAlgoState(symbol, self.tag.algoKey)
            # Remove if not invested
            if not security.Invested or symbolState == None or not symbolState.isInvested:
                continue

            positionSide = PositionSide.Long if security.Holdings.IsLong else PositionSide.Short
            currentTime: datetime = algorithm.Time
            mostRecentOrderTime: datetime = self.stateManager.getSymbolAlgoState(symbol, self.tag.algoKey).mostRecentOrderTime
            currentTime = currentTime.replace(tzinfo=mostRecentOrderTime.tzinfo)
            delta: timedelta =currentTime - mostRecentOrderTime
            daysDifference = delta.days

            if daysDifference > self.maxDays:
                Main.log(" In max days "+str(symbol)+" " +str(self.tag.algoKey)
                                + " with mostRecentOrderTime: " + str(mostRecentOrderTime)
                                + " currentTime " + str(currentTime)
                                + " daysDifference " + str(daysDifference))

                self.tag.description = "Max days passed: " + str(daysDifference)
                riskAdjustedTargets.append(TaggedPortfolioTarget(self.tag, symbol,
                                        RiskUtils.liquidateSymbolAlgoQuantity(symbolState.symbol,
                                                                              symbolState.algoKey)))


        return riskAdjustedTargets
