from QuantConnect import Symbol
from frameworkAlgo.state.keys import AlgoKey


class PositionChange:

    def __init__(self, symbol: Symbol, algoKey: AlgoKey):
        self.algoKey = algoKey
        self.symbol = symbol
        self.isBuy = False
        self.isSell = False
        self.isEntrySymbol = False
        self.isEntrySymbolAlgo = False
        self.isLiquidateSymbol = False
        self.isLiquidateSymbolAlgo = False
        self.isIncreasePositionSymbol = False
        self.isIncreasePositionSymbolAlgo = False
        self.isDecreasePositionSymbol = False
        self.isDecreasePositionSymbolAlgo = False
        self.isReversePositionSymbol = False
        self.isReversePositionSymbolAlgo = False

