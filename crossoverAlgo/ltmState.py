# region imports
import sys
from datetime import datetime, date
from random import randint

from AlgorithmImports import *
from AlgorithmImports import Globals
# endregion
# this will give an error, needs to be like above : from transaction import Transaction
from typing import List

from crossoverAlgo.securityState import SecurityState

# This isn't built out yet
class LtmState(SecurityState):

    def __init__(self, benchmark100DaySMA: SimpleMovingAverage,
                 fast: SimpleMovingAverage,
                 main: QCAlgorithm):
        super().__init__(main)

    def updateConsecutives(self):
        #if self.isFasterAboveFastCrossover():
        #    self.consecutiveFastAboveFaster = 0
        return None


    def benchmarkAbove100DaySMA(self):
        pass

    def is25DayAbove50DayCrossover(self):
        pass

    def debugState(self):
        pass
