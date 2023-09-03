# region imports

from datetime import datetime, date
from AlgorithmImports import *
# endregion
# this will give an error, needs to be like above : from transaction import Transaction
from typing import List
from abc import ABC, abstractmethod


class SecurityState(ABC):
    def __init__(self, main: QCAlgorithm):
        self.main = main
        self.previousActionDatetime: datetime = None
        self.previousAction: str = "none"
        self.holdings: float = 0
        self.symbol: Symbol = None


    @abstractmethod
    def updateConsecutives(self):
        return None

    def isSameDayAsPreviousAction(self, currentDate) -> bool:
        if self.previousActionDatetime is None:
            self.previousActionDatetime = currentDate
            return False
        elif self.previousActionDatetime.day == currentDate.day \
                and self.previousActionDatetime.month == currentDate.month \
                and self.previousActionDatetime.year == currentDate.year:
            return True
        else:
            return False

    def isCurrentlyShortOrUnheld(self) -> bool:
        if self.holdings <= 0:
            return True
        else:
            return False

    def isCurrentlyLongOrUnheld(self) -> bool:
        if self.holdings >= 0:
            return True
        else:
            return False


    def notPreviousActionBuy(self) -> bool:
        if self.previousAction == "short" or self.previousAction == "none" or self.previousAction == "liquidate":
            return True
        else:
            return False

    def notPreviousActionShort(self) -> bool:
        if self.previousAction == "buy" or self.previousAction == "none" or self.previousAction == "liquidate":
            return True
        else:
            return False
