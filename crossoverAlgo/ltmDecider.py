from QuantConnect.Algorithm import QCAlgorithm
from crossoverAlgo.longTermMomentumSetup import LongMomentumSetup
from crossoverAlgo.ltmState import LtmState
from crossoverAlgo.maxDrawdownExit import MaxDrawdownExit
from crossoverAlgo.crossoverSetups import Signal


# This isnt built yet see class LtmState
class LtmDecider():

    def __init__(self, chartState: LtmState, main: QCAlgorithm):
        self.chartState: LtmState = chartState
        self.main = main
        self.ltmSetup = LongMomentumSetup(chartState, main)
        self.maxDrawdownExit: MaxDrawdownExit = MaxDrawdownExit(chartState, main)

    def shouldBuy(self, shouldDebug: bool) -> Signal:

        if shouldDebug:
            self.chartState.debugState()

        result = self.ltmSetup.buySignal()
        return result

    def shouldShort(self, shouldDebug: bool) -> Signal:
        if shouldDebug:
            self.chartState.debugState()

        result = self.ltmSetup.shortSignal()
        return result

    def shouldLiquidate(self) -> Signal:
        return self.maxDrawdownExit.percentLiquidateSignal()


