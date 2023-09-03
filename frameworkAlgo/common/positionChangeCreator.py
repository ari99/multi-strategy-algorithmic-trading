from QuantConnect import Symbol
from QuantConnect.Orders import Order

from frameworkAlgo.mainHolder import Main
from frameworkAlgo.common.positionChange import PositionChange
from frameworkAlgo.ltm.taggedInsight import TaggedInsight
from frameworkAlgo.ltm.taggedPortfolioTarget import TaggedPortfolioTarget
from frameworkAlgo.state.keys import AlgoKey
from frameworkAlgo.state.stateManager import StateManager
from frameworkAlgo.state.states import SymbolState, SymbolAlgoState
from frameworkAlgo.state.tagModule import Tag


class PositionChangeCreator:

    # portfolio target should always have quantity as number of shares
    # used in TaggedImmediateExecution.Execute
    # and TargetCombiner.combineTargets
    @classmethod
    def createTargetChange(cls, target: TaggedPortfolioTarget) -> PositionChange:
        return cls.makeChange( target.Symbol, target.tag.algoKey, target.Quantity)

    # used in PercentPortfolioConstruction.DetermineTargetPercent and createPortfolioTarget
    @classmethod
    def createInsightChange(cls, insight: TaggedInsight):
        #return cls.makeChange(stateManager, insight.Symbol, insight.tag.algoKey, insight.Direction)
        pass

    # used by StateManager.updatePercent. Update percent is before updating SymbolStates
    @classmethod
    def createOrderChange(cls, order: Order) -> PositionChange:
        tag: Tag = Tag.fromStr(order.Tag)
        return cls.makeChange( order.Symbol, tag.algoKey, order.Quantity)


    @classmethod
    def makeChange(cls, symbol: Symbol,
                   algoKey: AlgoKey, quantity: float) -> PositionChange :
        change: PositionChange = PositionChange(symbol, algoKey)
        stateManager: StateManager = StateManager.getInstance()
        symbolState: SymbolState = stateManager.getSymbolStateOrDefault(symbol)
        symbolAlgoState: SymbolAlgoState = stateManager.getSymbolAlgoStateOrDefault(symbol, algoKey)
        currentSymbolQuantity: float = symbolState.runningTotalQuantity
        currentSymbolAlgoQuantity: float = symbolAlgoState.runningTotalQuantity
        newSymbolQuantity: float = quantity + currentSymbolQuantity
        newSymbolAlgoQuantity: float = quantity + currentSymbolAlgoQuantity

        cls.errorDecimals(" symbol ", quantity, currentSymbolQuantity, newSymbolQuantity)
        cls.errorDecimals(" symbolAlgo ", quantity, currentSymbolAlgoQuantity, newSymbolAlgoQuantity)

        if newSymbolQuantity == 0:
            change.isLiquidateSymbol = True

        if newSymbolAlgoQuantity == 0:
            change.isLiquidateSymbolAlgo = True

        if quantity > 0:
            change.isBuy = True

        if quantity < 0:
            change.isSell = True

        if (symbolState.isInvested
                and ((currentSymbolQuantity < 0 and newSymbolQuantity > 0) or
                (currentSymbolQuantity > 0 and newSymbolQuantity < 0)) ):
            change.isReversePositionSymbol = True

        if (symbolAlgoState.isInvested
                and ((currentSymbolAlgoQuantity < 0 and newSymbolAlgoQuantity > 0) or
                (currentSymbolAlgoQuantity > 0 and newSymbolAlgoQuantity < 0)) ):
            change.isReversePositionSymbolAlgo = True

        if not symbolState.isInvested and newSymbolQuantity != 0:
            change.isEntrySymbol = True

        if not symbolAlgoState.isInvested and newSymbolAlgoQuantity != 0:
            change.isEntrySymbolAlgo = True

        if (symbolState.isInvested
                and ((currentSymbolQuantity > 0 and newSymbolQuantity > currentSymbolQuantity) or
                     (currentSymbolQuantity < 0 and newSymbolQuantity < currentSymbolQuantity))):
            change.isIncreasePositionSymbol = True

        if (symbolAlgoState.isInvested and
                ((currentSymbolAlgoQuantity > 0 and newSymbolAlgoQuantity >  currentSymbolAlgoQuantity) or
                (currentSymbolAlgoQuantity < 0 and newSymbolAlgoQuantity < currentSymbolAlgoQuantity))):
            change.isIncreasePositionSymbolAlgo = True


        if (symbolState.isInvested
                and ((currentSymbolQuantity > 0 and newSymbolQuantity < currentSymbolQuantity and newSymbolQuantity > 0) or
                     (currentSymbolQuantity < 0 and newSymbolQuantity > currentSymbolQuantity and newSymbolAlgoQuantity < 0))):
            change.isDecreasePositionSymbol = True

        if (symbolAlgoState.isInvested and
                ((currentSymbolAlgoQuantity > 0 and newSymbolAlgoQuantity < currentSymbolAlgoQuantity and newSymbolAlgoQuantity > 0) or
                (currentSymbolAlgoQuantity < 0 and newSymbolAlgoQuantity > currentSymbolAlgoQuantity and newSymbolAlgoQuantity < 0))):
            change.isDecreasePositionSymbolAlgo = True

        return change



    @classmethod
    def errorDecimals(cls, description, changeQuantity,  currentQuantity,  newQuantity: float):
        if newQuantity > -1 and newQuantity < 1 and newQuantity != 0:
            Main.qcMain.Error(str(Main.qcMain.Time) + " decimal quantity in Position change >-1 <1 , "+
                              str(description)
                              + " change " + str(changeQuantity) + " current " + str(currentQuantity) +
                              " new total " + str(newQuantity))

