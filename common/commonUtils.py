from AlgorithmImports import *


class CommonUtils:

    def __init__(self, main: QCAlgorithm) -> None:
        self.sliceDebugCount = 0
        self.main = main

    def printObjects(self, rows: List) -> None:
        for row in rows:
            # print(row)
            self.main.Debug(vars(row))

    def printDictionary(self, dictionary: dict) -> None:
        for i in dictionary:
            self.main.Debug(i + ":   " + str(dictionary[i]))

    def debugSlice(self, slice:Slice) -> None:
        if self.sliceDebugCount % 5 == 0:
            self.sliceDebugCount += 1
            self.main.Debug("----------------------------slice " + str(slice.Time))
            for symbol, tradeBar in slice.Bars.items():
                tradeBar: TradeBar = tradeBar  # cant type hint a for loop
                self.main.Debug("   ----------------------------tradebar")
                self.main.Debug("       time " + str(tradeBar.Time))
                self.main.Debug("       symbol " + str(tradeBar.Symbol))
                self.main.Debug("       endTime " + str(tradeBar.EndTime))
                self.main.Debug("       close " + str(tradeBar.Close))
