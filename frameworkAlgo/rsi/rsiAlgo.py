from AlgorithmImports import *

from frameworkAlgo.algo import Algo
from frameworkAlgo.params import Params
from frameworkAlgo.securityChanger import IndicatorCreator, SecurityChanger, IndicatorKey
from frameworkAlgo.common.positionChange import PositionChange
from frameworkAlgo.risk.combinedRisk import CombinedRisk
from frameworkAlgo.risk.maxDaysRisk import MaxDaysRisk
from frameworkAlgo.risk.percentProfitProtectRisk import PercentProfitProtectRisk
from frameworkAlgo.ltm.ltmAlpha import LtmIndicatorCreator
from frameworkAlgo.ltm.percentPorfolioConstruction import PercentPortfolioConstruction
from frameworkAlgo.ltm.stopLossOnOrder import StopLossOnOrder
from frameworkAlgo.ltm.taggedImmediateExectution import TaggedImmediateExecution
from frameworkAlgo.rsi.rsiAlpha import RsiAlpha
from frameworkAlgo.state.keys import AlgoKey, SourceKey
from frameworkAlgo.state.stateManager import StateManager
from frameworkAlgo.state.tagModule import Tag
from frameworkAlgo.universe.ManualUniverseCreator import ManualUniverseCreator


# long term momentum algo from book
class RsiAlgo(Algo):
    def __init__(self, main: QCAlgorithm, securityChanger: SecurityChanger, stateManager: StateManager):
        super().__init__(main)
        self.algoKey = AlgoKey.RSI
        self.manualSymbols = [Symbol.Create("SPY", SecurityType.Equity, Market.USA),
                   #Symbol.Create("AMZN", SecurityType.Equity, Market.USA),
                   Symbol.Create("AAPL", SecurityType.Equity, Market.USA),
                   #Symbol.Create("CMG", SecurityType.Equity, Market.USA),
                   #Symbol.Create("DATA", SecurityType.Equity, Market.USA),
                   #Symbol.Create("DDOG", SecurityType.Equity, Market.USA)
                   ]
        self.main = main
        self.portfolioConstruction: IPortfolioConstructionModel = PercentPortfolioConstruction(self.main, stateManager)
        self.rsiAlpha: RsiAlpha = RsiAlpha(self.main, securityChanger, stateManager)
        self.universe: IUniverseSelectionModel = self.createUniverse()
        #self.riskManagement: IRiskManagementModel = MyTrailingStopRiskManagementModel(
        #                                               Tag(AlgoKey.RSI, SourceKey.RSI_RISK, ""), .25)
        #self.riskManagement: IRiskManagementModel = PercentProfitProtectRisk(
        #                                                Tag(AlgoKey.RSI, SourceKey.RSI_PROFIT_PERCENT, ""),
        #                                                stateManager, .04)
        self.riskManagement: IRiskManagementModel = CombinedRisk([
            MaxDaysRisk(Tag(AlgoKey.RSI, SourceKey.RSI_MAX_DAYS, ""), stateManager, Params.RSI_MAX_DAYS),
            PercentProfitProtectRisk( Tag(AlgoKey.RSI, SourceKey.RSI_PROFIT_PERCENT, ""),
                                      stateManager, Params.RSI_PERCENT_PROFIT)
        ])

        self.stopLossOnOrder: StopLossOnOrder = StopLossOnOrder(
                                                    Tag(AlgoKey.RSI, SourceKey.RSI_STOP, ""),
                                                    self.main, securityChanger, stateManager,
                                                    IndicatorKey.RSI_ALPHA_AVERAGE_TRUE_RANGE,
                                                    2,
                                                    AlgoKey.RSI)

        self.executionModel: IExecutionModel = TaggedImmediateExecution(stateManager)


    def getAlgoKey(self) -> AlgoKey:
        return self.algoKey
    def OnBeginningOfEndDay(self):
        tag: Tag = Tag(AlgoKey.RSI, SourceKey.RSI_END, "Liquidate on end day")
        self.main.Liquidate(tag=tag.toStr())
    def createUniverse(self):
        #return FirstUniverseClass(self.algoKey)
        return self.createManualUniverse()

    def createManualUniverse(self):
        return ManualUniverseCreator.createManualUniverse(self.algoKey, self.manualSymbols)

    def getUniverse(self) -> IUniverseSelectionModel:
        #self.AddUniverseSelection(EmaCrossUniverseSelectionModel())
        #self.AddUniverseSelection(FineFundamentalUniverseSelectionModel(self.SelectCoarse, self.SelectFine))
        return self.universe

    #https://github.com/QuantConnect/Lean/blob/master/Algorithm.Framework/Alphas/EmaCrossAlphaModel.py
    def getAlpha(self) -> IAlphaModel:
        return self.rsiAlpha

    # https://www.quantconnect.com/docs/v2/writing-algorithms/algorithm-framework/portfolio-construction/key-concepts
    def getPortfolioConstruction(self)-> IPortfolioConstructionModel:
        return self.portfolioConstruction

    # https://www.quantconnect.com/docs/v2/writing-algorithms/algorithm-framework/risk-management/key-concepts
    #https://github.com/QuantConnect/Lean/blob/master/Algorithm.Framework/Risk/TrailingStopRiskManagementModel.py
    def getRiskManagement(self)-> IRiskManagementModel:
        return self.riskManagement

    # https://www.quantconnect.com/docs/v2/writing-algorithms/algorithm-framework/execution/key-concepts
    def getExecution(self)-> IExecutionModel:
        return self.executionModel


    def OnOrderEvent(self, orderEvent: OrderEvent, orderChange: PositionChange) -> None:
        self.portfolioConstruction.OnOrderEvent(orderEvent)
        self.stopLossOnOrder.OnOrderEvent(orderEvent)

        return None

    def OnEndOfAlgorithm(self) -> None:
        self.main.Debug("IN ON END OF ALGO")
        # Liquidate needs to set up via schedule to run at beginning of last day
        #self.main.Liquidate(tag="LIQUIDATE: END OF ALGO")
        #self.main.Debug("LIQUIDATE ON END DONE")

    def doLiquidate(self):
        self.main.Liquidate(tag="LIQUIDATE: END OF ALGO")

    def OnData(self, slice: Slice):
        return None

    def OnSecuritiesChanged(self, changes: SecurityChanges) -> None:
        pass

    def getIndicatorCreator(self) -> IndicatorCreator:
        return LtmIndicatorCreator()


