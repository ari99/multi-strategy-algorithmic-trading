#region imports

from AlgorithmImports import *
#endregion

from abc import ABC, abstractmethod

from frameworkAlgo.securityChanger import IndicatorCreator
from frameworkAlgo.common.positionChange import PositionChange
from frameworkAlgo.state.keys import AlgoKey


class Algo(ABC):
    def __init__(self, main: QCAlgorithm):
        self.main = main

    @abstractmethod
    def getAlgoKey(self) -> AlgoKey:
        return None

    # https://www.quantconnect.com/docs/v2/writing-algorithms/algorithm-framework/universe-selection/key-concepts
    @abstractmethod
    def getUniverse(self) -> IUniverseSelectionModel:
        return None


    # https://www.quantconnect.com/docs/v2/writing-algorithms/algorithm-framework/alpha/key-concepts
    @abstractmethod
    def getAlpha(self) -> IAlphaModel:
        return None

    @abstractmethod
    def getPortfolioConstruction(self)-> IPortfolioConstructionModel:
        return None

    @abstractmethod
    def getRiskManagement(self)-> IRiskManagementModel:
        return None

    @abstractmethod
    def getExecution(self)-> IExecutionModel:
        return None


    @abstractmethod
    def OnOrderEvent(self, orderEvent: OrderEvent, orderChange: PositionChange) -> None:
        return None

    @abstractmethod
    def OnEndOfAlgorithm(self) -> None:
        return None

    @abstractmethod
    def OnData(self, slice: Slice):
        return None

    @abstractmethod
    def OnSecuritiesChanged(self, changes: SecurityChanges) -> None:
        return None

    @abstractmethod
    def getIndicatorCreator(self) -> IndicatorCreator:
        return None

    @abstractmethod
    def OnBeginningOfEndDay(self) -> None:
        return None