import pandas
from AlgorithmImports import *

from frameworkAlgo.mainHolder import Main
from frameworkAlgo.securityChanger import SecurityChanger, SymbolData, IndicatorKey
from frameworkAlgo.state.keys import AlgoKey
from frameworkAlgo.state.stateManager import StateManager
from frameworkAlgo.state.states import SymbolAlgoState
from frameworkAlgo.state.tagModule import Tag


# https://github.com/QuantConnect/Lean/blob/master/Algorithm.Framework/Risk/TrailingStopRiskManagementModel.py
# https://www.quantconnect.com/forum/discussion/3695/cancel-or-update-stop-market-order/p1
# https://www.quantconnect.com/forum/discussion/6314/keeping-track-of-multiple-stopmarketorders/p1
# https://www.quantconnect.com/forum/discussion/2943/making-a-trailing-stop-with-stopmarketorder/p1

class StopLossOnOrder():

    def __init__(self,tag: Tag,  main: QCAlgorithm,
                 securityChanger: SecurityChanger,
                 stateManager: StateManager,
                 indicatorKey: IndicatorKey,
                 indicatorMultiplier: float,
                 algoKey: AlgoKey):
        self.main = main
        self.securityChanger: SecurityChanger = securityChanger
        self.tag: Tag = tag
        self.algoKey: AlgoKey = algoKey
        self.stateManager: StateManager = stateManager
        self.indicatorKey = indicatorKey
        self.indicatorMultiplier = indicatorMultiplier

    # statemanager is called before this
    def OnOrderEvent(self, orderEvent: OrderEvent) -> None:
        order: Order = self.main.Transactions.GetOrderById(orderEvent.OrderId)

        if orderEvent.Status == OrderStatus.Filled:
            #self.main.Debug("===============Order Filled Event===================")
            #self.main.Debug(f"{self.main.Time}: {order.Type}: {orderEvent}")
            symbol = orderEvent.Symbol
            holding: SecurityHolding =  self.main.Portfolio.get(symbol)
            #symbols = [x.Value for x in self.main.Securities.Keys]
            # 1 is span: The span over which to retrieve recent historical data
            tag: Tag = Tag.fromStr(order.Tag)
            orderAlgoKey = tag.algoKey
            # this state has already been updated
            symbolState: SymbolAlgoState = self.stateManager.getSymbolAlgoState(symbol, orderAlgoKey)
            if symbolState is not None and symbolState.isInvested and orderAlgoKey == self.algoKey:
                Main.log("New position, removing stop losses for " + str(symbol) + " then going to add stop loss")
                self.stateManager.cancelSymbolAlgoOrders(symbol, orderAlgoKey, " new position entry order event for "+
                                                           str(symbol) + " algokey "+ str(self.algoKey) )
                Main.log("Adding stop loss for " + str(symbol) + " " +str(orderAlgoKey), logLevel=3, symbol=symbol)
                self.addStopLoss(symbol, symbolState.runningTotalQuantity, order)
            elif orderAlgoKey == self.algoKey or orderAlgoKey==AlgoKey.COMMON:
                self.stateManager.cancelSymbolAlgoOrders(symbol, orderAlgoKey, " liquidate position order event for "+
                                                           str(symbol) + " algokey "+ str(self.algoKey) )


    def addStopLoss(self, symbol: Symbol, orderQuantity: float, order: Order):
        Main.log("Setting up stop loss for "+ str(symbol) + " " + str(Main.qcMain.Time) , symbol=symbol)
        symbolState: SymbolAlgoState = self.stateManager.getSymbolAlgoState(symbol, self.algoKey)
        indicatorValue = self.getIndicatorValue(symbol)
        close = self.getClose(symbol)
        isLong = symbolState.isLong
        isShort = symbolState.isShort

        Main.log("holding is invested, close:  " + str(close) +
                        " indicatorValue " + str(indicatorValue)
                        + " isLong " + str(isLong)
                        + " isShort " + str(isShort))

        if indicatorValue == None or close == None:
            raise Exception("Both shouldnt be none: indicatorValue " + str(indicatorValue)
            +" close " + str(close) + " symbol " + str(symbol))

        if isLong:
            stopPrice = close - (self.indicatorMultiplier * indicatorValue)
        elif isShort:
            stopPrice = close + (self.indicatorMultiplier * indicatorValue)
        else:
            raise Exception("Neither long nor short - cant determine the direction of ordert for stop loss")


        if close and indicatorValue:
            self.tag.description = "Stop loss Order created on "+ str(symbol.Value)+ \
                                   " stop price " + str(stopPrice) + \
                                    " quantity " + str(-orderQuantity) + \
                                    " created time " + str(self.main.Time) + \
                                   " from purchase at " + str(order.Time) + \
                                    " original price " + str(order.Price) + \
                                    " atr value " + str(indicatorValue) + \
                                    " atr mult " + str(self.indicatorMultiplier) + \
                                    " atr delta " + str(self.indicatorMultiplier * indicatorValue)

            orderTicket: OrderTicket = self.main.StopMarketOrder(
                                          symbol,
                                          -orderQuantity,
                                          stopPrice,  # close * 0.7,
                                          tag=self.tag.toStr())

            Main.log("Created stop order ticket: " + str(symbol) +
                            " " + str(self.algoKey) + " " + str(orderTicket.OrderId)
                            + " quantity " + str(-orderQuantity), logLevel=3)

            self.stateManager.addOpenOrder(symbol, self.algoKey, orderTicket.OrderId)
        else:
            raise Exception("all should have close and indicatorvalue")


    def getIndicatorValue(self,  symbol: Symbol):
        symbolData: SymbolData = self.securityChanger.symbolDataBySymbol.get(symbol)
        if symbolData:
            symbolPrice = symbolData.security.Price
            atr = symbolData.indicators[self.indicatorKey]
            indicatorValue = atr.Current.Value
            return indicatorValue
        else:
            self.main.Error("securityChanger symbol "+str(symbol) +" data doesnt exist in StopLossOnOrder "
                            + str(self.algoKey))
            return None


    def getClose(self, symbol: Symbol):
        hist: pandas.DataFrame = self.main.History(symbol, 1, Resolution.Daily)
        if symbol in hist.index:
            Main.log(" Symbol in history index")
            Main.log("close is: " + str(hist.iloc[0]['close']))  # hist[symbol].close))
            return hist.iloc[0]['close']
        else:
            self.main.Error(" Symbol not in history index")
            return None

    def OnSecuritiesChanged(self, algorithm: QCAlgorithm, changes: SecurityChanges) -> None:
        # Thist is only called on change of universe, not for buys/sells
        # Security additions and removals are pushed here.
        # This can be used for setting up algorithm state.
        # changes.AddedSecurities:
        # changes.RemovedSecurities:
        for security in changes.AddedSecurities:
            holding: SecurityHolding =  algorithm.Portfolio.get(security.Symbol)
            Main.log(" security added  " + str(security.Symbol) + "  " +str(holding.Quantity))

        for security in changes.RemovedSecurities:
            holding: SecurityHolding =  algorithm.Portfolio.get(security.Symbol)
            Main.log(" security REMOVED  " + str(security.Symbol) + "  " +str(holding.Quantity))




