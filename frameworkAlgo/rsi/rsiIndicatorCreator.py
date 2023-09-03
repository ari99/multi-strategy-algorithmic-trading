
from AlgorithmImports import *

from frameworkAlgo.params import Params
from frameworkAlgo.securityChanger import IndicatorKey, IndicatorCreator


class RsiIndicatorCreator(IndicatorCreator):

    def __init__(self):
        super().__init__()
        self.rsiPeriod = Params.RSI_PERIOD
        self.averageTrueRangerPeriod = Params.ATR_PERIOD
        self.adxPeriod = Params.ADX_PERIOD

    def createIndicators(self) -> Dict[IndicatorKey, IndicatorBase]:
        rsi = RelativeStrengthIndex(self.rsiPeriod)
        atr = AverageTrueRange(self.averageTrueRangerPeriod, MovingAverageType.Simple)
        adx = AverageDirectionalIndex(self.adxPeriod)

        indicators: Dict[IndicatorKey, IndicatorBase] = {
                IndicatorKey.RSI: rsi,
                IndicatorKey.RSI_ALPHA_AVERAGE_TRUE_RANGE: atr,
                IndicatorKey.RSI_ALPHA_AVERAGE_DIRECTIONAL_INDEX: adx
        }

        return indicators


