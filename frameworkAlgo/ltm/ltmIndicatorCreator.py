
from AlgorithmImports import *

from frameworkAlgo.mainHolder import Main
from frameworkAlgo.params import Params
from frameworkAlgo.securityChanger import IndicatorKey, IndicatorCreator


class LtmIndicatorCreator(IndicatorCreator):

    def __init__(self):
        super().__init__()
        self.fastPeriod = Params.LTM_SMA_FAST_PERIOD
        self.slowPeriod = Params.LTM_SMA_SLOW_PERIOD
        self.benchmarkSmaPeriod = Params.LTM_BENCH_SMA
        self.averageTrueRangerPeriod = Params.ATR_PERIOD
        self.adxPeriod = Params.ADX_PERIOD

    def createIndicators(self) -> Dict[IndicatorKey, IndicatorBase]:
        Main.log(" Creating indicator with fast " + str(self.fastPeriod) + " slow "+ str(self.slowPeriod),
                 logLevel=4)
        bechmarkSma = SimpleMovingAverage(self.benchmarkSmaPeriod)
        Fast = SimpleMovingAverage(self.fastPeriod)
        Slow = SimpleMovingAverage(self.slowPeriod)
        atr = AverageTrueRange(self.averageTrueRangerPeriod, MovingAverageType.Simple)
        adx = AverageDirectionalIndex(self.adxPeriod)
        indicators: Dict[IndicatorKey, IndicatorBase] = \
            {
                IndicatorKey.FAST: Fast,
                IndicatorKey.SLOW: Slow,
                IndicatorKey.BENCHMARK_SMA: bechmarkSma,
                IndicatorKey.LTM_AVERAGE_TRUE_RANGE: atr,
                IndicatorKey.LTM_AVERAGE_DIRECTIONAL_INDEX: adx

            }
        return indicators
