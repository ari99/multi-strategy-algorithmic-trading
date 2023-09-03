from crossoverAlgo.exits import Exit
from crossoverAlgo.crossoverSetups import Setup, Signal

from QuantConnect.Algorithm import QCAlgorithm

from crossoverAlgo.crossoverState import CrossState
from crossoverAlgo.ltmState import LtmState


# this isnt built out yet ,  LtmState class is missing method implementations
#1 - Long Trend High Momentum #pg 136
class LongMomentumSetup(Setup):
    def __init__(self, chartState: LtmState, main: QCAlgorithm):
        super().__init__(chartState, main)
        self.chartState = chartState

    def buySignal(self) -> Signal:
        result = Signal()

        if self.canBuy() and \
            self.chartState.benchmarkAbove100DaySMA() and \
                self.chartState.is25DayAbove50DayCrossover():
            result.shouldBuy = True
            result.reason = " Long Momentum "
        else:
            result.shouldBuy = False

        return result

    def shortSignal(self)-> Signal:
        result = Signal()
        result.shouldShort = False
        return result
        ''' Turn of shorts for now
        if self.canShort() \
                and self.chartState.isSlowAboveFastCrossover():
            result.shouldShort = True
            result.reason = " Slow Above Fast Cross "
        else:
            result.shouldShort = False
        return result'''

# https://github.com/QuantConnect/Lean/blob/master/Algorithm.Framework/Risk/MaximumDrawdownPercentPerSecurity.py

