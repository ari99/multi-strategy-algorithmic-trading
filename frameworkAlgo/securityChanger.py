from abc import ABC, abstractmethod

from AlgorithmImports import *

from frameworkAlgo.mainHolder import Main
from frameworkAlgo.state.stateManager import StateManager
from frameworkAlgo.state.states import SymbolAlgoState

class IndicatorKey(Enum):
    FAST = 1
    SLOW = 2
    BENCHMARK_SMA = 3
    LTM_AVERAGE_TRUE_RANGE = 4
    LTM_AVERAGE_DIRECTIONAL_INDEX = 5
    RSI = 6
    RSI_ALPHA_AVERAGE_TRUE_RANGE = 7
    RSI_ALPHA_AVERAGE_DIRECTIONAL_INDEX = 8


class IndicatorCreator(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def createIndicators(self) -> Dict[IndicatorKey, IndicatorBase]:
        return None


# https://github.com/QuantConnect/Lean/blob/master/Algorithm.Framework/Alphas/EmaCrossAlphaModel.py
class SecurityChanger():

    def __init__(self, indicatorCreators: List[IndicatorCreator],
                 stateManager: StateManager):
        self.indicatorCreators: List[IndicatorCreator] = indicatorCreators
        self.symbolDataBySymbol: Dict[Symbol, SymbolData] = {}
        self.removedSymbolsPendingOrders: List[Symbol] = []
        self.stateManager = stateManager

    def symbolHasPendingOrders(self, symbol: Symbol):
        states: List[SymbolAlgoState] = self.stateManager.getSymbolAlgoStates(symbol)
        for state in states:
            if state.orderExecutedButNotFilled == True:
                return True

        return False

    def OnSecuritiesChanged(self, algorithm: QCAlgorithm, changes: SecurityChanges) -> None:

        for removedSymbol in self.removedSymbolsPendingOrders:
            if not self.symbolHasPendingOrders(removedSymbol):
                self.removedSymbolsPendingOrders.remove(removedSymbol
                                                        )
        Main.log(" ------On securities changed in SecurityChanger")

        for removedSecurity in changes.RemovedSecurities:
            removedSymbol: Symbol = removedSecurity.Symbol
            Main.log("Removed " + str(removedSymbol))

            if self.symbolHasPendingOrders(removedSymbol):
                self.removedSymbolsPendingOrders.append(removedSymbol)
            else:
                if Main.inSyms(removedSymbol):
                    Main.log(" Removing symbol from symboldata  "
                             + str(removedSymbol), 3)

                    data = self.symbolDataBySymbol.pop(removedSymbol, None)
                    if data is not None:
                        # clean up our consolidators
                        data.dispose()

        for addedSecurity in changes.AddedSecurities:
            Main.log("Added " + str(addedSecurity.Symbol))

            symbolData = self.symbolDataBySymbol.get(addedSecurity.Symbol)
            if symbolData is None:
                if Main.inSyms(addedSecurity.Symbol):
                    Main.log(" Adding symbol to symboldata  " + str(addedSecurity.Symbol), 3)

                symbolData = SymbolData(algorithm, addedSecurity, self.indicatorCreators)  # self.indicatorTypes)
                self.symbolDataBySymbol[addedSecurity.Symbol] = symbolData
            '''else:
                # a security that was already initialized was re-added, reset the indicators
                for symbol in self.symbolDataBySymbol:
                    for indicator in self.symbolDataBySymbol[symbol].indicators:
                        self.symbolDataBySymbol[symbol].indicators[indicator].Reset()
                        algorithm.WarmUpIndicator(symbol,
                                                  self.symbolDataBySymbol[symbol].indicators[indicator],
                                                  Resolution.Daily)
            '''

    def resetSymbolIndicators(self, symbol: Symbol):
        if symbol in self.symbolDataBySymbol:
            self.symbolDataBySymbol[symbol].doReset()


class SymbolData:
    def __init__(self, algorithm: QCAlgorithm, security,
                 indicatorCreators: List[IndicatorCreator]):
        self.algorithm = algorithm
        self.security = security
        self.symbol = security.Symbol
        self.indicators: Dict[IndicatorKey, IndicatorBase] = self.createIndicators(indicatorCreators)
        self.consolidators: List[IDataConsolidator] = []
        # self.consolidator = TradeBarConsolidator(1)
        # algorithm.SubscriptionManager.AddConsolidator(self.symbol, self.consolidator)

        for indicator in self.indicators:
            # algorithm.SubscriptionManager.AddConsolidator(self.symbol, self.consolidator)
            # self.consolidator = TradeBarConsolidator(1)
            consolidator: IDataConsolidator = algorithm.ResolveConsolidator(security.Symbol, Resolution.Daily)
            self.consolidators.append(consolidator)
            algorithm.SubscriptionManager.AddConsolidator(self.symbol, consolidator)
            algorithm.RegisterIndicator(self.symbol, self.indicators[indicator], consolidator)
            if Main.inSyms(self.symbol) and indicator == IndicatorKey.LTM_AVERAGE_TRUE_RANGE:
                algorithm.Debug("Warming up indicator " + str(indicator) + " for " + str(self.symbol))
            algorithm.WarmUpIndicator(self.symbol, self.indicators[indicator], Resolution.Daily)

    def createIndicators(self, indicatorCreators: List[IndicatorCreator]) -> None:
        result: Dict[IndicatorKey, IndicatorBase] = {}
        for indicatorCreator in indicatorCreators:
            indicators: Dict[IndicatorKey, IndicatorBase] = indicatorCreator.createIndicators()
            for key in indicators:
                result[key] = indicators[key]
        return result


    def doReset(self) -> None:
        Main.log(" Restting all indicators")
        for indicatorKey in self.indicators:
            indicator: IndicatorBase = self.indicators[indicatorKey]
            indicator.Reset()
            self.algorithm.WarmUpIndicator(self.symbol, indicator)

    def dispose(self) -> None:
        for consolidator in self.consolidators:
            self.algorithm.SubscriptionManager.RemoveConsolidator(self.symbol, consolidator)
