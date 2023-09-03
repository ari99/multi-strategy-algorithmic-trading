import pandas

from AlgorithmImports import *

from frameworkAlgo.securityChanger import SecurityChanger, IndicatorKey, SymbolData, IndicatorCreator
from enum import Enum



class AlphaUtils:
    def __init__(self, main: QCAlgorithm):
        self.main: QCAlgorithm = main

    def daysHigherClose(self, symbol: Symbol, numDays: int) -> bool:
        bars: pandas.DataFrame = self.main.History(symbol, TimeSpan.FromDays(numDays+10), Resolution.Daily)

        if symbol in bars.index and len(bars.index) >= numDays:

            for i in range(numDays-1):
                if bars.iloc[i]['close'] > bars.iloc[i+1]['close']:
                    return False
            return True
        else:
            self.main.Error(" ERROR Symbol " + str(symbol) + " not in history "
            " index alphaUtils daysHigherClose OR " + str(len(bars.index))  + "  < " +str(numDays ))
            return False

    def daysLowerClose(self, symbol: Symbol, numDays: int) -> bool:
        bars: pandas.DataFrame = self.main.History(symbol, numDays, Resolution.Daily)
        if symbol in bars.index and len(bars.index) >= numDays:
            for i in range(numDays-1): # next check here values , make sure it is using rigtht dates
                '''self.main.Debug(" Num days " + str(numDays) + " DAYS LOWER closses false if "
                                + str(bars.index.get_level_values(1)[i]) + "  "
                                + str(bars.iloc[i]['close']) + "   >  "
                                + str(bars.iloc[i+1]['close']) + "  " + str(bars.index.get_level_values(1)[i+1]) )'''
                # i is the day before i+1
                if bars.iloc[i]['close'] < bars.iloc[i+1]['close']:
                    return False
            return True
        else:
            self.main.Error(" ERROR Symbol " + str(symbol) + " not in history "
                        " index alphaUtils daysHigherClose OR " + str(len(bars.index)) + "  < " + str(numDays))
            self.main.Debug("----- \n" + str(bars))

            return False


    def isBenchmarkAboveSma(self, securityChanger: SecurityChanger) -> bool:
        bechmarkSymbol = Symbol.Create("SPY", SecurityType.Equity, Market.USA)
        benchmarkSymbolData: SymbolData = securityChanger.symbolDataBySymbol.get(bechmarkSymbol)
        if benchmarkSymbolData:
            benchmarkPrice = benchmarkSymbolData.security.Price
            benchmarkIndicator = benchmarkSymbolData.indicators[IndicatorKey.BENCHMARK_SMA]
            if benchmarkPrice > benchmarkIndicator.Current.Value:
                return True


        return False

    def isBenchmarkBellowSma(self, securityChanger: SecurityChanger) -> bool:
        bechmarkSymbol = Symbol.Create("SPY", SecurityType.Equity, Market.USA)
        benchmarkSymbolData: SymbolData = securityChanger.symbolDataBySymbol.get(bechmarkSymbol)
        if benchmarkSymbolData:
            benchmarkPrice = benchmarkSymbolData.security.Price
            benchmarkIndicator = benchmarkSymbolData.indicators[IndicatorKey.BENCHMARK_SMA]

            if benchmarkPrice < benchmarkIndicator.Current.Value:
                return True


        return False
