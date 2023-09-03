
from AlgorithmImports import *
#from Selection.FundamentalUniverseSelectionModel import FundamentalUniverseSelectionModel

import random
from typing import List

from QuantConnect.Algorithm.Framework.Selection import FundamentalUniverseSelectionModel
from QuantConnect.Indicators import ExponentialMovingAverage, RateOfChange

from frameworkAlgo.mainHolder import Main
from frameworkAlgo.params import Params



# class used to improve readability of the coarse selection function
class CrossoverRocUniverseSelectionData:
    def __init__(self, symbol:Symbol, fastPeriod: int, slowPeriod: int, rocPeriod: int):
        self.Symbol: Symbol = symbol
        self.FastEma: ExponentialMovingAverage = ExponentialMovingAverage(fastPeriod)
        self.SlowEma: ExponentialMovingAverage = ExponentialMovingAverage(slowPeriod)
        self.MyRoC: RateOfChange = RateOfChange(rocPeriod)

    @property
    def Fast(self) -> float:
        return float(self.FastEma.Current.Value)

    @property
    def Slow(self) -> float:
        return float(self.SlowEma.Current.Value)

    @property
    def RoC(self) -> float:
        return float(self.MyRoC.Current.Value)

    # computes an object score of how much large the fast is than the slow
    @property
    def ScaledLongDelta(self) -> float:
        return (self.Fast - self.Slow) / ((self.Fast + self.Slow) / 2)

    # updates the EMAFast and EMASlow indicators, returning true when they're both ready
    def Update(self, time, value) -> bool:
        return self.SlowEma.Update(time, value) & self.FastEma.Update(time, value) & self.MyRoC.Update(time, value)
