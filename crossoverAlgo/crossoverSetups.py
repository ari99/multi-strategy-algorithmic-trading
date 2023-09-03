from abc import ABC, abstractmethod
from QuantConnect.Algorithm import QCAlgorithm
from crossoverAlgo.crossoverState import CrossState
from crossoverAlgo.securityState import SecurityState

class Signal():
    def __init__(self):
        self.shouldBuy: bool = False
        self.shouldShort: bool = False
        self.shouldLiquidate: bool = False
        self.reason: str = ""


class Setup(ABC):
    def __init__(self, chartState: SecurityState, main: QCAlgorithm):
        self.chartState = chartState
        self.main = main

    @abstractmethod
    def buySignal(self)-> Signal:
        return None

    @abstractmethod
    def shortSignal(self)-> Signal:
        return None

    def canBuy(self)-> bool:
        if self.chartState.isCurrentlyShortOrUnheld() and self.chartState.notPreviousActionBuy():
            return True
        else:
            return False

    def canShort(self) -> bool:
        if self.chartState.isCurrentlyLongOrUnheld() and self.chartState.notPreviousActionShort():
            return True
        else:
            return False


class FastAboveSlowCrossoverSetup(Setup):
    def __init__(self, chartState: CrossState, main: QCAlgorithm):
        super().__init__(chartState, main)
        self.chartState: CrossState = chartState # repeated here for linting typing/linting

    def buySignal(self)-> Signal:
        result= Signal()
        if self.canBuy() \
                and (self.chartState.isFastAboveSlowCrossover()):
            self.main.Debug(" FAST ABOVE SLOW CROSSOVER ")
            self.main.Debug(str(self.chartState.notPreviousActionBuy()))
            result.shouldBuy = True
            result.reason = " Fast Above Slow Cross "
        else:
            result.shouldBuy = False

        return result

    def shortSignal(self)-> Signal:
        result= Signal()
        if self.canShort() \
                and self.chartState.isSlowAboveFastCrossover():
            result.shouldShort = True
            result.reason = " Slow Above Fast Cross "
        else:
            result.shouldShort = False
        return result





class FasterAboveSlowAfterLiquidateSetup(Setup):
    def __init__(self, chartState: CrossState, main: QCAlgorithm):
        super().__init__(chartState, main)
        self.chartState: CrossState = chartState # repeated here for typing/linting


    def buySignal(self)-> Signal:
        result= Signal()
        if self.canBuy() and \
                self.chartState.isFasterAboveSlowCrossover() and \
                self.chartState.previousAction == "liquidate" and self.chartState.fastAboveSlow():

            self.main.Debug(" Faster above slow crossover ")
            self.main.Debug(str(self.chartState.notPreviousActionBuy()))
            result.shouldBuy = True
            result.reason = " Faster Above Slow Cross "
        else:
            result.shouldBuy = False

        return result


    def shortSignal(self)-> Signal:
        result = Signal()
        if self.canShort() and \
                self.chartState.isSlowAboveFasterCrossover() and \
                self.chartState.previousAction == "liquidate" and \
                self.chartState.slowAboveFast():
            result.shouldShort = True
            result.reason = " Slow Above Faster Cross "
        else:
            result.shouldShort = False

        return result

