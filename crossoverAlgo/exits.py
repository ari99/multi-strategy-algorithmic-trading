from abc import ABC, abstractmethod

from QuantConnect.Algorithm import QCAlgorithm

from crossoverAlgo.crossoverState import CrossState
from crossoverAlgo.crossoverSetups import Signal
from crossoverAlgo.securityState import SecurityState


class Exit(ABC):
    def __init__(self, chartState: SecurityState, main: QCAlgorithm):
        self.chartState = chartState
        self.main = main

    @abstractmethod
    def liquidateSignal(self)-> Signal:
        return None


class MaxUnrealizedExit(Exit):
    def __init__(self, chartState: CrossState, main: QCAlgorithm):
        super().__init__(chartState, main)
        self.maxUnrealizedPLDollar = -5000
        self.maxUnrealizedPLPercent = -.25


    def dollarLiquidateSignal(self)-> Signal:
        result = Signal()
        if self.main.Portfolio[self.chartState.symbol].UnrealizedProfit <= self.maxUnrealizedPLDollar:
            result.shouldLiquidate = True
            result.reason = "Dollar LIQUIDATE: UNREALIZED_PROFIT<=" + str(self.maxUnrealizedPLDollar)
        else:
            result.shouldLiquidate = False

        return result

    def percentLiquidateSignal(self)-> Signal:
        result = Signal()
        if self.main.Portfolio[self.chartState.symbol].UnrealizedProfitPercent <= self.maxUnrealizedPLPercent:
            result.shouldLiquidate = True
            result.reason = "Percent LIQUIDATE: UNREALIZED_PROFIT<=" + str(self.maxUnrealizedPLPercent)
        else:
            result.shouldLiquidate = False

        return result