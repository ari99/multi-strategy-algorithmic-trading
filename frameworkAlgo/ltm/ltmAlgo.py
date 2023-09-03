from AlgorithmImports import *

from frameworkAlgo.algo import Algo
from frameworkAlgo.params import Params
from frameworkAlgo.securityChanger import IndicatorCreator, SecurityChanger, IndicatorKey
from frameworkAlgo.common.positionChange import PositionChange
from frameworkAlgo.ltm.ltmAlpha import LtmAlpha, LtmIndicatorCreator
from frameworkAlgo.ltm.percentPorfolioConstruction import PercentPortfolioConstruction
from frameworkAlgo.ltm.stopLossOnOrder import StopLossOnOrder
from frameworkAlgo.ltm.taggedImmediateExectution import TaggedImmediateExecution
from frameworkAlgo.risk.trailingStopRisk import MyTrailingStopRiskManagementModel
from frameworkAlgo.state.keys import SourceKey, AlgoKey
from frameworkAlgo.state.stateManager import StateManager
from frameworkAlgo.state.tagModule import Tag
from frameworkAlgo.universe.ManualUniverseCreator import ManualUniverseCreator


# long term momentum algo
class LtmAlgo(Algo):
    def __init__(self, main: QCAlgorithm, securityChanger: SecurityChanger, stateManager: StateManager):
        super().__init__(main)
        self.main = main
        self.algoKey = AlgoKey.LTM
        self.manualSymbols = [Symbol.Create("SPY", SecurityType.Equity, Market.USA),
                   Symbol.Create("AMZN", SecurityType.Equity, Market.USA),
                   #Symbol.Create("AAPL", SecurityType.Equity, Market.USA),
                   #Symbol.Create("CMG", SecurityType.Equity, Market.USA),
                   #Symbol.Create("DATA", SecurityType.Equity, Market.USA),
                   #Symbol.Create("DDOG", SecurityType.Equity, Market.USA)
                   ]
        self.portfolioConstruction: IPortfolioConstructionModel = PercentPortfolioConstruction(self.main, stateManager)
        self.ltmAlpha: LtmAlpha = LtmAlpha(self.main, securityChanger, stateManager)
        self.universe: IUniverseSelectionModel = self.createUniverse()
        self.riskManagement: IRiskManagementModel = MyTrailingStopRiskManagementModel(
            Tag(AlgoKey.LTM, SourceKey.LTM_RISK, ""), stateManager, Params.LTM_TRAILING_STOP_PERCENT)
        self.stopLossOnOrder: StopLossOnOrder = StopLossOnOrder(Tag(AlgoKey.LTM, SourceKey.LTM_STOP, ""),
                                                                self.main, securityChanger, stateManager,
                                                                IndicatorKey.LTM_AVERAGE_TRUE_RANGE,
                                                                Params.LTM_STOP_LOSS_MULTIPLIER,
                                                                AlgoKey.LTM)
        self.executionModel: IExecutionModel = TaggedImmediateExecution(stateManager)


    def getAlgoKey(self) -> AlgoKey:
        return self.algoKey

    def OnBeginningOfEndDay(self):
        tag: Tag = Tag(AlgoKey.LTM, SourceKey.LTM_END, "Liquidate on end day")
        self.main.Transactions.CancelOpenOrders()
        self.main.Liquidate(tag=tag.toStr())

    def createUniverse(self):
        #return FirstUniverseClass(self.algoKey)
        return self.createManualUniverse()


    def createManualUniverse(self):
        return ManualUniverseCreator.createManualUniverse(self.algoKey, self.manualSymbols)


    def getUniverse(self) -> IUniverseSelectionModel:
        return self.universe

    #https://github.com/QuantConnect/Lean/blob/master/Algorithm.Framework/Alphas/EmaCrossAlphaModel.py
    def getAlpha(self) -> IAlphaModel:
        return self.ltmAlpha

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
        self.portfolioConstruction.OnOrderEvent(orderEvent) # todo change to use orderChange
        self.stopLossOnOrder.OnOrderEvent(orderEvent)
        # remove the previous max holdings value if the
        # position was reversed or the poistion was liquidated
        self.riskManagement.OnOrderEvent(orderEvent, orderChange)
        return None

    def OnEndOfAlgorithm(self) -> None:
        self.main.Debug("IN ON END OF ALGO")
        # Luqidate needs to be set up via schedule to run at the beginning of last day
        #self.main.Liquidate(tag="LIQUIDATE: END OF ALGO")
        #self.main.Debug("LIQUIDATE ON END DONE")

    def doLiquidate(self):
        self.main.Liquidate(tag="LIQUIDATE: END OF ALGO")

    def OnData(self, slice: Slice):
        #self.main.Debug("In ondata--" )
        #self.handleSplits(slice)
        return None

    def OnSecuritiesChanged(self, changes: SecurityChanges) -> None:
        self.ltmAlpha.OnSecuritiesChanged(self.main, changes)

    def getIndicatorCreator(self) -> IndicatorCreator:
        return LtmIndicatorCreator()


