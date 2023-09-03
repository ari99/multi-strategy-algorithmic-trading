
from AlgorithmImports import *

from frameworkAlgo.mainHolder import Main
from frameworkAlgo.params import Params
from frameworkAlgo.common.positionChange import PositionChange
from frameworkAlgo.state.keys import AlgoKey, SourceKey
from frameworkAlgo.state.states import SymbolState, SymbolAlgoState
from frameworkAlgo.state.tagModule import Tag


class StateManager:
    instance = None
    def __init__(self,  main: QCAlgorithm):
        self.main = main
        self.percentUsed: float = 0
        self.percent = Params.POSITION_PERCENT
        self.symbolStates: Dict[Symbol, SymbolState] = {}
        self.combinedUniverse: Set[Symbol] =set()
        self.algoUniverses: Dict[AlgoKey, List[Symbol]] = {}

    @classmethod
    def getInstance(cls, main: QCAlgorithm = None):
        if cls.instance is None and main is not None:
            cls.instance = cls(main)
        return  cls.instance

    def addUniverse(self, algoKey: AlgoKey, symbols: List[Symbol]) -> None:
        self.removePreviousAlgoSymbolsFromUniverse(algoKey)
        if algoKey not in self.algoUniverses:
            self.algoUniverses[algoKey] = []
        for symbol in symbols:
            if symbol not in self.combinedUniverse:
                self.combinedUniverse.add(symbol)
                self.algoUniverses[algoKey].append(symbol)

    def removePreviousAlgoSymbolsFromUniverse(self, algoKey: AlgoKey) -> None:
        if algoKey in self.algoUniverses:
            for symbol in self.algoUniverses.get(algoKey):
                self.combinedUniverse.remove(symbol)

    def addOpenOrder(self, symbol: Symbol, algoKey: AlgoKey, orderId: int) -> None:
        self.symbolStates[symbol].symbolAlgoStates[algoKey].openOrders.append(orderId)

    def factorStateQuantitys(self, symbol: Symbol, splitFactor: float) -> None:
        if symbol in self.symbolStates:
            algoStates: Dict[AlgoKey, SymbolAlgoState] = self.symbolStates[symbol].symbolAlgoStates
            # update symbol algo states
            for algoKey in algoStates:
                previousQuantity: float = algoStates[algoKey].mostRecentOrderQuantity
                previousTotalQuantity: float = algoStates[algoKey].runningTotalQuantity
                if previousQuantity is not None:
                    self.symbolStates[symbol].symbolAlgoStates[algoKey].mostRecentOrderQuantity = previousQuantity * splitFactor
                if previousTotalQuantity is not None:
                    self.symbolStates[symbol].symbolAlgoStates[algoKey].runningTotalQuantity = previousTotalQuantity * splitFactor
            # update symbol state
            previousTotalQuantity: float = self.symbolStates[symbol].runningTotalQuantity
            if previousTotalQuantity is not None:
                self.symbolStates[symbol].runningTotalQuantity =previousTotalQuantity * splitFactor


    def OnOrderEvent(self, orderEvent: OrderEvent, orderChange: PositionChange) -> None:
        order: Order = self.main.Transactions.GetOrderById(orderEvent.OrderId)

        if orderEvent.Status == OrderStatus.Filled:
            symbol = orderEvent.Symbol
            # from OrderDirection enum buy=0, sell=1,hold=2
            holding: SecurityHolding = self.main.Portfolio.get(symbol)
            #holding.Quantity
            #holding.AbsoluteQuantity
            Main.log("updating percent ", logLevel=3)
            self.updatePercent(holding, symbol, order)
            Main.log("updating symbol algo state " + str(symbol.Value) + " "+ str(order.Tag), logLevel=3)
            self.updateSymbolAlgoStates(symbol, Tag.fromStr(order.Tag), #holding,
                                        order)
            Main.log("updating symbol state " + str(symbol.Value) + " "+ str(order.Tag), logLevel=3)
            #has to be last to delete symbol from common liquidate
            self.updateSymbolState(symbol, order, orderChange)


    def updateSymbolState(self, symbol: Symbol,  order: Order, orderChange: PositionChange) -> None:
        if symbol in self.symbolStates and orderChange.isLiquidateSymbol:
            Main.log(" Liquidating symbol, deleteing state " + str(symbol.Value), logLevel=3)
            self.symbolStates.pop(symbol, None)
        else:
            if symbol not in self.symbolStates:
                self.symbolStates[symbol] = SymbolState(symbol=symbol)

            previousState = self.getSymbolState(symbol)
            previousTotalQuantity: float = 0
            if previousState:
                previousTotalQuantity = previousState.runningTotalQuantity

            newRunningTotal = previousTotalQuantity + order.Quantity
            self.symbolStates[symbol].isLong = (newRunningTotal > 0)
            self.symbolStates[symbol].isInvested = (newRunningTotal != 0)
            self.symbolStates[symbol].isShort = (newRunningTotal < 0)
            self.symbolStates[symbol].runningTotalQuantity = newRunningTotal
            # this method is called when an order is filled
            self.symbolStates[symbol].orderExecutedButNotFilled = False

    def updateSymbolAlgoStates(self, symbol: Symbol, tag: Tag,
                               order: Order) -> None:

        previousState = self.getSymbolAlgoState(symbol, tag.algoKey)
        previousTotalQuantity: float = 0
        if previousState:
            previousTotalQuantity = previousState.runningTotalQuantity

        newRunningTotal = previousTotalQuantity + order.Quantity

        newSymbolState: SymbolAlgoState = SymbolAlgoState(symbol)
        newSymbolState.algoKey = tag.algoKey
        newSymbolState.isLong = (newRunningTotal > 0)
        newSymbolState.isInvested = (newRunningTotal != 0)
        newSymbolState.isShort = (newRunningTotal < 0)
        newSymbolState.mostRecentAbsoluteCost = (order.AbsoluteQuantity * order.Price)
        newSymbolState.mostRecentOrderTime = order.Time
        newSymbolState.mostRecentOrderQuantity = order.Quantity
        newSymbolState.runningTotalQuantity = newRunningTotal
        # this method is called when an order is filled
        newSymbolState.orderExecutedButNotFilled = False
        self.setSymbolAlgoState(newSymbolState)


    def getSymbolAlgoStateOrDefault(self, symbol: Symbol, algoKey: AlgoKey)-> SymbolAlgoState:
        symbolAlgoState: SymbolAlgoState = SymbolAlgoState(symbol)
        symbolAlgoState.algoKey = algoKey

        if symbol not in self.symbolStates:
            self.symbolStates[symbol] = SymbolState(symbolAlgoState = symbolAlgoState)
            return symbolAlgoState
        elif symbol in self.symbolStates and algoKey not in self.symbolStates[symbol].symbolAlgoStates:
            self.symbolStates[symbol].symbolAlgoStates[algoKey] = symbolAlgoState
            return symbolAlgoState
        else:
            return self.symbolStates[symbol].symbolAlgoStates[algoKey]

    def getSymbolAlgoState(self, symbol: Symbol, algoKey: AlgoKey) -> SymbolAlgoState :

        if symbol not in self.symbolStates:
            return None
        elif symbol in self.symbolStates and algoKey not in self.symbolStates[symbol].symbolAlgoStates:
            return None
        else:
            return self.symbolStates[symbol].symbolAlgoStates[algoKey]

    def getSymbolState(self, symbol: Symbol) -> SymbolState :
        if symbol not in self.symbolStates:
            return None
        else:
            return self.symbolStates[symbol]

    def getSymbolStateOrDefault(self, symbol: Symbol) -> SymbolState:
        if symbol not in self.symbolStates:
            return SymbolState(symbol=symbol)
        else:
            return self.symbolStates[symbol]



    def setSymbolState(self, symbolState: SymbolState) -> None:
        symbol = symbolState.symbol
        self.symbolStates[symbol] = symbolState


    def setSymbolAlgoState(self, symbolAlgoState: SymbolAlgoState) -> None:
        Main.log(" Before setting symbolAlgoState for " + str(symbolAlgoState.symbol)
                    + " . "+ str(symbolAlgoState.algoKey) +
                    " to " + str(vars(symbolAlgoState)))
        symbol = symbolAlgoState.symbol
        algoKey = symbolAlgoState.algoKey
        if symbol not in self.symbolStates:
            self.symbolStates[symbol] = SymbolState(symbolAlgoState=symbolAlgoState)
            self.symbolStates[symbol].symbolAlgoStates[algoKey] = symbolAlgoState
        elif symbol in self.symbolStates \
                and algoKey not in self.symbolStates[symbol].symbolAlgoStates:
            self.symbolStates[symbol].symbolAlgoStates[algoKey] = symbolAlgoState
        else:
           self.symbolStates[symbol].symbolAlgoStates[algoKey] = symbolAlgoState


    def debugPercentUsed(self, holding, symbolState, order: Order, newQuantity) -> None:
        if symbolState is not None:
            symStr = ("  symbolState.isInvested " + str(symbolState.isInvested) +
                "  symbolState.isShort " + str(symbolState.isShort) +
                "  symbolState.isLong " + str(symbolState.isLong) +
                " symbolState.quantity " + str(symbolState.runningTotalQuantity))
        else:
            symStr = ""

        Main.log("percent used  " + str(self.percentUsed) +
                        "  holding.Invested " + str(holding.Invested) +
                        "  holding.Quantity " + str(holding.Quantity) +
                        "  orderDirection " + str(order.Direction) +
                        " order.quantity " + str(order.Quantity) +
                        " new quantity " + str(newQuantity)+ symStr)


    def updatePercent(self, holding: SecurityHolding, symbol: Symbol, order: Order) -> None:
        orderDirection: int = order.Direction
        Main.log(" Order tag is " + str(order.Tag))
        tag= Tag.fromStr(order.Tag)
        # This is the symbol state before this order
        previousSymbolState: SymbolState = self.getSymbolState(symbol)

        # TODO limit buys and sells to only current direction if invested with different algo?
        # There is no symbol state for split or other liquidations, convert to using holdings
        # Main.log(" BEFORE updating percent " + str(symbolState.symbol.Value) + " . " + str(symbolState.algoKey) +
        #"  symbole state: "+ str(vars(symbolState)), logLevel=3)
        if previousSymbolState is not None:
            newQuantity = previousSymbolState.runningTotalQuantity + order.Quantity
            if holding.Invested and (previousSymbolState.isLong or not previousSymbolState.isInvested) \
                    and orderDirection == OrderDirection.Buy:
                Main.log("longing - incrementing percent used  ", logLevel=3)
                self.percentUsed += self.percent
            elif holding.Invested and (previousSymbolState.isShort or not previousSymbolState.isInvested) \
                    and orderDirection == OrderDirection.Sell:
                Main.log("shorting -  incrementing percent used  ", logLevel=3)
                self.percentUsed += self.percent
            elif (previousSymbolState.isShort and orderDirection == OrderDirection.Buy and holding.IsLong) or \
                (previousSymbolState.isLong and orderDirection == OrderDirection.Sell and holding.IsShort) :
                Main.log("Percent - not changing because switching short to long or vice versa", logLevel=3)
                # do nothing because its switching from long to short or vice versa
            elif not previousSymbolState.isInvested and \
                (orderDirection == OrderDirection.Buy or orderDirection == OrderDirection.Sell):
                Main.log(" Incrementing percent used, not invested and buying or shorting: ", logLevel=3)
                self.percentUsed += self.percent
            else:
                Main.log(" Decrementing percent used , invested " + str(holding.Invested)
                         + " islong " +  str(holding.IsLong)
                         + " IsShort " + str(holding.IsShort)
                         + " previous quantity " + str(previousSymbolState.runningTotalQuantity)
                         + " new quantity " + str(newQuantity)
                         , logLevel=3 )
                self.percentUsed -= self.percent

            self.debugPercentUsed(holding, previousSymbolState, order, newQuantity)
        elif orderDirection != OrderDirection.Hold:
            Main.log("Incresing Percent - no previousSymbolState and order direction does not equal hold - ", logLevel=3)
            self.percentUsed += self.percent
        else:
            Main.log(" UpdatePercent, uknown action", logLevel=3)


    def cancelSymbolOrders(self, symbol: Symbol, tag: Tag) -> None:
        Main.log("Canceling symbol orders " + str(symbol))
        self.main.Transactions.CancelOpenOrders(symbol, tag=tag.toStr())
        if symbol in self.symbolStates:
            symbolAlgoStates: Dict[AlgoKey, SymbolAlgoState] = self.symbolStates[symbol].symbolAlgoStates
            for algoKey in symbolAlgoStates:
                self.symbolStates[symbol].symbolAlgoStates[algoKey].openOrders = []


    def cancelSymbolAlgoOrders(self, symbol: Symbol, algoKey: AlgoKey, cancelTag: str) -> None:
        Main.log("Canceling symbol orders " + str(symbol) + " " + str(algoKey))
        symbolState: SymbolAlgoState = self.getSymbolAlgoState(symbol, algoKey)
        if symbolState:
            for orderId in self.getSymbolAlgoState(symbol, algoKey).openOrders:
                self.main.Transactions.CancelOrder(orderId, orderTag=cancelTag)
                Main.log("Did cancel symbol order " + str(symbol)
                         + " "+ str(algoKey) + " order id " + str(orderId) + " tag " + cancelTag, logLevel=3 )

            self.symbolStates[symbol].symbolAlgoStates[algoKey].openOrders = []

    def getSymbolAlgoStates(self, symbol) -> List[SymbolAlgoState] :
        states: List[SymbolAlgoState] = []
        if symbol in self.symbolStates:
            algoStates: Dict[AlgoKey, SymbolAlgoState]= self.symbolStates[symbol].symbolAlgoStates
            for algoKey in algoStates:
                states.append(algoStates[algoKey])

        return states




