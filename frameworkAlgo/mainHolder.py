import datetime

from AlgorithmImports import QCAlgorithm, Symbol
from QuantConnect import SecurityType, Market


class Main():
    qcMain: QCAlgorithm = None
    minLevel = 3

    @staticmethod
    def setMain(qcMain: QCAlgorithm):
        qcMain.Debug("Setting qcMain ");
        Main.qcMain = qcMain

    @classmethod
    def log(cls, message: str, logLevel=2, symbol=None):
        #time: datetime = cls.qcMain.Time
        if logLevel is not None and logLevel >= cls.minLevel or \
                symbol is not None and cls.inSyms(symbol):
            cls.qcMain.Debug(message)

    @staticmethod
    def inSyms(symbol: Symbol):
        syms = []
        if symbol in syms:
            return True
        else:
            return False

