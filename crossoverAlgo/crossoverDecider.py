from QuantConnect.Algorithm import QCAlgorithm

from crossoverAlgo.crossoverState import CrossState
from crossoverAlgo.exits import MaxUnrealizedExit
from crossoverAlgo.crossoverSetups import FastAboveSlowCrossoverSetup, FasterAboveSlowAfterLiquidateSetup, Signal


class CrossDecider():

    def __init__(self, chartState: CrossState, main: QCAlgorithm):
        self.chartState = chartState
        self.main = main
        self.fastAboveSlowSetup = FastAboveSlowCrossoverSetup(chartState, main)
        self.fasterAboveSlowSetup = FasterAboveSlowAfterLiquidateSetup(chartState, main)
        self.maxUnrealizedExit = MaxUnrealizedExit(chartState,main)

    def shouldBuy(self, shouldDebug: bool) -> Signal:
        if shouldDebug:
            self.chartState.debugState()

        result= self.fastAboveSlowSetup.buySignal()
        if result.shouldBuy == False:
            result= self.fasterAboveSlowSetup.buySignal()

        return result

    def shouldShort(self, shouldDebug: bool) -> Signal:
        if shouldDebug:
            self.chartState.debugState()

        result: Signal = self.fastAboveSlowSetup.shortSignal()
        if result.shouldShort == False:
            result = self.fasterAboveSlowSetup.shortSignal()

        return result

    def shouldLiquidate(self) -> Signal:
        return self.maxUnrealizedExit.liquidateSignal()


