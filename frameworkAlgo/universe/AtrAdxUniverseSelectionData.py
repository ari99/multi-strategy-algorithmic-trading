from AlgorithmImports import *


# class used to improve readability of the coarse selection function
class AtrAdxUniverseSelectionData:
    def __init__(self, symbol, atrPeriod, adxPeriod):
        self.Symbol = symbol
        self.averageTrueRange = AverageTrueRange(atrPeriod)
        self.averageDirectionalIndex = AverageDirectionalIndex(adxPeriod)
        self.currentValue = 0

    @property
    def ATR(self) -> float:
        return float(self.averageTrueRange.Current.Value)

    @property
    def ADX(self) -> float:
        return float(self.averageDirectionalIndex.Current.Value)

    #     average true price range percentage over last 10 days is
    #     three percent or more of the closing price of the stock- for volatility
    @property
    def atrPercent(self) -> float:
        return abs(self.averageTrueRange.Current.Value / self.currentValue)

    # updates the indicators, returning true when they're both ready
    def Update(self, time, value) -> bool:
        self.currentValue = value
        return (self.averageTrueRange.Update(time, value)
                & self.averageDirectionalIndex.Update(time, value))
