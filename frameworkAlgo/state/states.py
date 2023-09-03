from typing import Dict, List

from QuantConnect import Symbol

from frameworkAlgo.mainHolder import Main
from frameworkAlgo.state.keys import AlgoKey, SourceKey
from datetime import datetime




class SymbolAlgoState():
    def __init__(self, symbol: Symbol):
        self.symbol: Symbol = symbol
        self.algoKey: AlgoKey = None
        self.isLong: bool = False
        self.isShort: bool = False
        self.isInvested: bool = False
        self.openOrders: List = []
        self.mostRecentAbsoluteCost: float = None
        self.mostRecentOrderTime: datetime = None
        self.mostRecentOrderQuantity: float = None
        self.runningTotalQuantity: float = 0
        # I saw that we make an order and it may not get filled for multiple
        # days for some reason.
        # Also the security may get removed from the universe before it gets filled
        # Use this variable to prevent additional order from being placed
        # or prevent logic which is run post removal from universe
        self.orderExecutedButNotFilled: bool = False

    def debug(self):
        Main.log("symbolState: "
                        "  symbol " + str(self.symbol.Value) +
                        "  .algoKey " + str(self.algoKey) +
                        "  .isShort " + str(self.isShort) +
                        "  .isLong " + str(self.isLong) +
                        "  .isInvested " + str(self.isInvested) +
                        "  .openOrders " + str(self.openOrders) +
                        "  .mostRecentAbsoluteCost " + str(self.mostRecentAbsoluteCost) +
                        "  .mostRecentOrderTime " + str(self.mostRecentOrderTime) +
                        "  .mostRecentOrderQuantity " + str(self.mostRecentOrderQuantity) +
                        "  .runningTotalQuantity " + str(self.runningTotalQuantity)
                     )


class SymbolState():
    def __init__(self, symbol: Symbol = None, symbolAlgoState: SymbolAlgoState = None):
        if symbolAlgoState is not None:
            self.symbol = symbolAlgoState.symbol
            self.runningTotalQuantity: float = symbolAlgoState.runningTotalQuantity
            self.isLong = symbolAlgoState.isLong
            self.isShort = symbolAlgoState.isShort
            self.isInvested = symbolAlgoState.isInvested
            self.symbolAlgoStates: Dict[AlgoKey, SymbolAlgoState] = {symbolAlgoState.algoKey: symbolAlgoState}
            self.orderExecutedButNotFilled: bool = symbolAlgoState.orderExecutedButNotFilled
        else:
            self.symbol = symbol
            self.runningTotalQuantity: float = 0
            self.isLong = False
            self.isShort = False
            self.isInvested = False
            self.symbolAlgoStates: Dict[AlgoKey, SymbolAlgoState] = {}
            self.orderExecutedButNotFilled: bool = False


class CrossoverSymbolAlgoState(SymbolAlgoState):
    def __init__(self, symbol):
        super().__init__(symbol)
        self.previouslyFastIsOverSlow = False
        self.previouslySlowIsOverFast = False

