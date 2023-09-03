# region imports
from AlgorithmImports import *
# endregion
# this will give an error, needs to be like above : from transaction import Transaction
from typing import List

from crossoverAlgo.securityState import SecurityState


class CrossState(SecurityState):
    def __init__(self, faster: SimpleMovingAverage,
                 fast: SimpleMovingAverage, slow: SimpleMovingAverage,
                 main: QCAlgorithm):
        super().__init__(main)

        self.consecutiveFasterAboveSlow = 0
        self.consecutiveFastAboveSlow = 0
        self.consecutiveSlowAboveFast = 0
        self.consecutiveSlowAboveFaster = 0
        self.consecutiveFasterAboveFast = 0
        self.consecutiveFastAboveFaster = 0
        self.faster = faster
        self.fast = fast
        self.slow = slow
        self.tolerance = 0.00025

    def isFastAboveFasterCrossover(self) -> bool:
        if self.fastAboveFaster() and self.consecutiveFastAboveFaster == 0:
            return True
        else:
            return False

    def isFasterAboveFastCrossover(self) -> bool:
        if self.fasterAboveFast() and self.consecutiveFasterAboveFast == 0:
            return True
        else:
            return False

    def fastAboveFaster(self) -> bool:
        if self.fast.Current.Value > self.faster.Current.Value * (1 + self.tolerance):
            return True
        else:
            return False

    def fasterAboveFast(self) -> bool:
        if self.faster.Current.Value > self.fast.Current.Value * (1 + self.tolerance):
            return True
        else:
            return False

    def isFastAboveSlowCrossover(self) -> bool:
        if self.fastAboveSlow() and self.consecutiveFastAboveSlow == 0:
            return True
        else:
            return False

    def isSlowAboveFastCrossover(self) -> bool:
        if self.slowAboveFast() and self.consecutiveSlowAboveFast == 0:
            return True
        else:
            return False

    def isFasterAboveSlowCrossover(self) -> bool:
        if self.fasterAboveSlow() and self.consecutiveFasterAboveSlow == 0:
            return True
        else:
            return False

    def isSlowAboveFasterCrossover(self) -> bool:
        if self.slowAboveFaster() and self.consecutiveSlowAboveFaster == 0:
            return True
        else:
            return False


    def fastAboveSlow(self) -> bool:
        if self.fast.Current.Value > self.slow.Current.Value * (1 + self.tolerance):
            return True
        else:
            return False

    def fasterAboveSlow(self) -> bool:
        if self.faster.Current.Value > self.slow.Current.Value * (1 + self.tolerance):
            return True
        else:
            return False

    def slowAboveFast(self) -> bool:
        if self.slow.Current.Value > self.fast.Current.Value * (1 + self.tolerance):
            return True
        else:
            return False

    def slowAboveFaster(self) -> bool:
        if self.slow.Current.Value > self.faster.Current.Value * (1 + self.tolerance):
            return True
        else:
            return False

    def updateConsecutives(self) -> None:

        if self.isFasterAboveFastCrossover():
            self.consecutiveFastAboveFaster = 0

        if self.isFastAboveFasterCrossover():
            self.consecutiveFasterAboveFast = 0

        if self.isFastAboveSlowCrossover():
            self.consecutiveSlowAboveFast = 0


        if self.isFasterAboveSlowCrossover():
            self.consecutiveSlowAboveFaster = 0

        if self.isSlowAboveFastCrossover():
            self.consecutiveFastAboveSlow = 0

        if self.isSlowAboveFasterCrossover():
            self.consecutiveFasterAboveSlow = 0

        if self.fastAboveSlow():
            self.consecutiveFastAboveSlow += 1

        if self.fasterAboveSlow():
            self.consecutiveFasterAboveSlow += 1

        if self.slowAboveFast():
            self.consecutiveSlowAboveFast += 1

        if self.slowAboveFaster():
            self.consecutiveSlowAboveFaster += 1

        if self.fastAboveFaster():
            self.consecutiveFastAboveFaster += 1

        if self.fasterAboveFast():
            self.consecutiveFasterAboveFast += 1


    def debugState(self) -> None:
        debugStr: str = "\n isCurrentlyShortOrUnheld " + str(self.isCurrentlyShortOrUnheld()) + \
                        "\n notPreviousActionBuy " + str(self.notPreviousActionBuy()) + \
                        "\n isFastAboveSlowCrossover " + str(self.isFastAboveSlowCrossover()) + \
                        "\n isFasterAboveSlowCrossover " + str(self.isFasterAboveSlowCrossover()) + \
                        "\n previousAction " + self.previousAction + \
                        "\n fastAboveSlow " + str(self.fastAboveSlow()) + \
                        "\n fasterAboveSlow " + str(self.fasterAboveSlow()) + \
                        "\n consecutiveFasterAboveSlow " + str(self.consecutiveFasterAboveSlow) + \
                        "\n consecutiveFastAboveSlow " + str(self.consecutiveFastAboveSlow) + \
                        "\n consecutiveSlowAboveFast " + str(self.consecutiveSlowAboveFast) + \
                        "\n consecutiveSlowAboveFaster " + str(self.consecutiveSlowAboveFaster)

        self.main.Debug(debugStr)