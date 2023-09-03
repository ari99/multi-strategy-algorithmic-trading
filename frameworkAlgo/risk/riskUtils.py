
from QuantConnect import Symbol

from frameworkAlgo.state.keys import AlgoKey
from frameworkAlgo.state.stateManager import StateManager
from frameworkAlgo.state.states import SymbolAlgoState, SymbolState


class RiskUtils:

    @classmethod
    def liquidateSymbolAlgoQuantity(cls, symbol: Symbol , algoKey: AlgoKey) -> float:
        stateManager: StateManager = StateManager.getInstance()
        state: SymbolAlgoState = stateManager.getSymbolAlgoState(symbol, algoKey)
        return ( -1 * state.runningTotalQuantity)

    @classmethod
    def liquidateSymbolQuantity(cls, symbol: Symbol , algoKey: AlgoKey) -> float:
        stateManager: StateManager = StateManager.getInstance()
        state: SymbolState = stateManager.getSymbolState(symbol)
        return ( -1 * state.runningTotalQuantity)


