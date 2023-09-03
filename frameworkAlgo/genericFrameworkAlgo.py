

from AlgorithmImports import *

from frameworkAlgo.algo import Algo
from frameworkAlgo.securityChanger import SecurityChanger
from frameworkAlgo.common.positionChange import PositionChange
from frameworkAlgo.common.positionChangeCreator import PositionChangeCreator
from frameworkAlgo.ltm.ltmAlgo import LtmAlgo
from frameworkAlgo.ltm.ltmIndicatorCreator import LtmIndicatorCreator
from frameworkAlgo.state.stateManager import StateManager


#endregion

# This uses QuantConnect's algorithm framework - https://www.quantconnect.com/docs/v2/writing-algorithms/algorithm-framework
# https://github.com/QuantConnect/Lean/blob/master/Algorithm.Python/BasicTemplateFrameworkAlgorithm.py
# This is no longer being used and contains deprecated function call parameters
class GenericFrameworkAlgorithm():
    def __init__(self):
        self.main = None
        self.algos: List[Algo] = []

    def Initialize(self, main: QCAlgorithm) -> None:
        self.main = main
        self.main.SetStartDate(2014, 1, 1)
        #self.main.SetStartDate(2020, 1, 1)
        self.main.SetEndDate(2022, 12, 8)
        # Set the starting cash balance to $100,000 USD
        self.main.SetCash(100000)
        stateManager = StateManager.getInstance(self.main)
        indicatorCreators = [LtmIndicatorCreator()]
        securityChanger = SecurityChanger(indicatorCreators, stateManager)

        self.algos = [ LtmAlgo(main, securityChanger, stateManager)]

        for algo in self.algos:
            self._addUniverseSelection(algo)
            self._addAlpha(algo)
            self._setPortfolioConstruction(algo)
            self._addRiskManagement(algo)
            self._setExecution(algo)

    def OnOrderEvent(self, orderEvent: OrderEvent) -> None:
        order:Order = self.main.Transactions.GetOrderById(orderEvent.OrderId)
        orderChange: PositionChange = PositionChangeCreator.createOrderChange(order)

        if orderEvent.Status == OrderStatus.Filled:
            self.main.Debug("===============Order Filled Event===================")
            self.main.Debug(f"{self.main.Time}: {order.Type}: {orderEvent}  -- ---- " + str(order.Tag))
        for algo in self.algos:
            algo.OnOrderEvent(orderEvent, orderChange)

    def OnEndOfAlgorithm(self) -> None:
        for algo in self.algos:
            algo.OnEndOfAlgorithm()

    def OnData(self, slice: Slice):
        for algo in self.algos:
            algo.OnData(slice)


    # https://www.quantconnect.com/docs/v2/writing-algorithms/algorithm-framework/universe-selection/key-concepts
    def _addUniverseSelection(self, algo: Algo ):
        self.main.AddUniverseSelection(algo.getUniverse())

    # https://www.quantconnect.com/docs/v2/writing-algorithms/algorithm-framework/alpha/key-concepts
    def _addAlpha(self, algo: Algo ):
        #self.main.AddAlpha(RsiAlphaModel())
        self.main.AddAlpha(algo.getAlpha())

    # https://github.com/QuantConnect/Lean/blob/master/Algorithm.Framework/Portfolio/EqualWeightingPortfolioConstructionModel.py
    # https://www.quantconnect.com/docs/v2/writing-algorithms/algorithm-framework/portfolio-construction/key-concepts
    def _setPortfolioConstruction(self, algo: Algo ):
        #self.main.SetPortfolioConstruction(EqualWeightingPortfolioConstructionModel())
        self.main.SetPortfolioConstruction(algo.getPortfolioConstruction())

    # https://www.quantconnect.com/docs/v2/writing-algorithms/algorithm-framework/risk-management/key-concepts
    def _addRiskManagement(self, algo: Algo):
        self.main.AddRiskManagement(algo.getRiskManagement())

    # https://www.quantconnect.com/docs/v2/writing-algorithms/algorithm-framework/execution/key-concepts
    def _setExecution(self, algo: Algo ):
        self.main.SetExecution(algo.getExecution())








