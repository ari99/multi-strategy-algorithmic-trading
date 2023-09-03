#region imports

from AlgorithmImports import *

from frameworkAlgo.algo import Algo
from frameworkAlgo.mainHolder import Main
from frameworkAlgo.params import Params
from frameworkAlgo.securityChanger import SecurityChanger, IndicatorCreator
from frameworkAlgo.targetCombiner import TargetCombiner
from frameworkAlgo.common.positionChange import PositionChange
from frameworkAlgo.common.positionChangeCreator import PositionChangeCreator
from frameworkAlgo.ltm.ltmAlgo import LtmAlgo
from frameworkAlgo.ltm.ltmIndicatorCreator import LtmIndicatorCreator
from frameworkAlgo.ltm.taggedImmediateExectution import TaggedImmediateExecution
from frameworkAlgo.ltm.taggedInsight import TaggedInsight
from frameworkAlgo.ltm.taggedPortfolioTarget import TaggedPortfolioTarget
from frameworkAlgo.rsi.rsiAlgo import RsiAlgo
from frameworkAlgo.rsi.rsiIndicatorCreator import RsiIndicatorCreator
from frameworkAlgo.state.keys import AlgoKey, SourceKey
from frameworkAlgo.state.stateManager import StateManager
from frameworkAlgo.state.tagModule import Tag
#endregion


class MyFramework():
    """
        This is a custom framework based on QuantConnect's algorithm framework but with the ability
        to support multiple strategies. Also has improved tagging and statistics.
    """
    def __init__(self):
        self.main = None
        self.algos: List[Algo] = []
        self.compositUniverse: CompositeUniverseSelectionModel = None
        self.securityChanger: SecurityChanger = None
        self.indicatorCreators: List[IndicatorCreator] = []
        self.stateManager: StateManager = None
        self.targetCombiner = None

    # https://github.com/QuantConnect/Lean/blob/master/Algorithm.Python/BasicTemplateFrameworkAlgorithm.py
    def Initialize(self, main: QCAlgorithm) -> None:
        self.main = main
        Params.setup(main)
        self.stateManager = StateManager.getInstance(self.main)

        self.main.SetStartDate(2014, 1, 1)
        #self.main.SetStartDate(2021, 1, 1)
        self.main.SetEndDate(2022, 12, 8)
        # Set the starting cash balance to $100,000 USD
        self.main.SetCash(100000)
        self.main.SetBrokerageModel(BrokerageName.QuantConnectBrokerage)
        self.main.SetWarmUp(100)

        indicatorCreators = [LtmIndicatorCreator(),
                             RsiIndicatorCreator()
                             ]
        self.securityChanger = SecurityChanger(indicatorCreators, self.stateManager)

        self.algos = [RsiAlgo(main, self.securityChanger, self.stateManager),
                      LtmAlgo(main, self.securityChanger, self.stateManager)
                      ]
        self.targetCombiner: TargetCombiner = TargetCombiner(self.main, self.algos, self.stateManager)


        self.setUniverse()

        self.main.Schedule.On(self.main.DateRules.On(self.main.EndDate.year,
                                                     self.main.EndDate.month, self.main.EndDate.day),
                              self.main.TimeRules.At(0, 0),
                              self.OnBeginningOfEndDay)


    def OnBeginningOfEndDay(self):
        for algo in self.algos:
            algo.OnBeginningOfEndDay()

    def OnOrderEvent(self, orderEvent: OrderEvent) -> None:
        order:Order = self.main.Transactions.GetOrderById(orderEvent.OrderId)
        if orderEvent.Status == OrderStatus.Filled:
            Main.log("===============Order Filled Event, previous percent: "
                            + str(self.stateManager.percentUsed)+"===================", logLevel=3)
            Main.log(f"{self.main.Time}: {order.Type}: {orderEvent}  -- ---- " + str(order.Tag), logLevel=3)

            orderChange: PositionChange = PositionChangeCreator.createOrderChange(order)
            # make sure statemanager is updated before stoploss because stoploss uses state manager.isInvested
            self.stateManager.OnOrderEvent(orderEvent, orderChange)

            for algo in self.algos:
                algo.OnOrderEvent(orderEvent, orderChange)

    def OnEndOfAlgorithm(self) -> None:
        for algo in self.algos:
            algo.OnEndOfAlgorithm()


    def OnData(self, slice: Slice):
        for algo in self.algos:
            algo.OnData(slice)

        self.frameworkOnData(slice)
        self.handleSplits(slice)

    def OnSecuritiesChanged(self, changes: SecurityChanges) -> None:
        for algo in self.algos:
            algo.OnSecuritiesChanged(changes)

        self.securityChanger.OnSecuritiesChanged(self.main, changes )


    # https://www.quantconnect.com/forum/discussion/13012/price-data-error-even-though-checking-data-containskey/p1
    def onlySliceHas(self, targets: List[TaggedInsight], slice: Slice):
        result: List [TaggedInsight] = []
        for target in targets:
            if slice.ContainsKey(target.Symbol) and target.Symbol in slice.Bars:
                result.append(target)
        return result

    def frameworkOnData(self, slice: Slice):
        # check for iswarming up:
        # https://www.quantconnect.com/forum/discussion/14759/initial-positions-when-going-from-initialisation-to-realtime-mode/p1
        # https://www.quantconnect.com/docs/v2/writing-algorithms/historical-data/warm-up-periods
        if not self.main.IsWarmingUp:
            insights: List[TaggedInsight] = self.createInsightsFromAlphas(slice)
            sliceHasSymbolInsights: List[TaggedInsight] = self.onlySliceHas(insights, slice)
            allTargets: List[PortfolioTarget] = self.targetCombiner.createTargets(sliceHasSymbolInsights)
            self.executeTargets(allTargets)
        else:
            pass
            #Main.log("Algo is warming up  " + str(slice.Time))


    def executeTargets(self, targets: List[TaggedPortfolioTarget]):
        executionModel: TaggedImmediateExecution = self.algos[0].getExecution()
        executionModel.Execute(self.main, targets)


    def createInsightsFromAlphas(self, slice: Slice) -> List[TaggedInsight]:
        result: List[TaggedInsight] = []
        for algo in self.algos:
            alpha = algo.getAlpha()
            insights = alpha.Update(self.main, slice)
            if len(insights) > 0:
                Main.log("-------------Found " + str(len(insights)) + " insights for slice " + str(slice.Time))
            for insight in insights:
                result.append(insight)

        return result

    def setUniverse(self):
        self.main.UniverseSettings.Resolution = Resolution.Daily
        #self.main.SetUniverseSelection(FirstUniverseClass())
        #self.main.AddUniverseSelection(FirstUniverseClass())
        for algo in self.algos:
            self.main.AddUniverseSelection(algo.getUniverse())
        # https://www.quantconnect.com/docs/v2/writing-algorithms/algorithm-framework/universe-selection/key-concepts
        '''
        I think the only way to use universes is to pass Universe objects to AddUniverseSelection
        if not isinstance(algo.getUniverse(), NullUniverseSelectionModel):
            if self.compositUniverse is not None:
                self.compositUniverse.AddUniverseSelection(algo.getUniverse())
            else:
                self.compositUniverse = CompositeUniverseSelectionModel(algo.getUniverse())
        '''

    def makeIndicatorCreators(self)-> List[IndicatorCreator]:
        result: List[IndicatorCreator] = []
        for algo in self.algos:
            result.append(algo.getIndicatorCreator())
        return result

    # https://www.quantconnect.com/datasets/quantconnect-us-equity-security-master/examples
    # https://www.quantconnect.com/docs/v2/writing-algorithms/indicators/key-concepts#09-Reset-Indicators
    # https://www.quantconnect.com/docs/v2/writing-algorithms/indicators/manual-indicators#06-Warm-Up-Indicators
    def handleSplits(self, slice: Slice):
        '''
        month: int = slice.Time.date().month
        year: int = slice.Time.date().year
        day: int = slice.Time.date().day

        if slice.Time.date().year == 2022 and slice.Time.date().month == 6:
            self.main.Debug("======================")
            self.main.Debug(" month " + str(month))
            self.main.Debug(" day " + str(day))


        split = slice.Splits.get(self.symbol)

        '''
        # https://stackoverflow.com/questions/41641449/how-do-i-annotate-types-in-a-for-loop
        split: Split
        for splitKey in slice.Splits.GetKeys:
            split: Split = slice.Splits.get(splitKey)
            splitSymbol: Symbol = split.Symbol
            holding: SecurityHolding = self.main.Portfolio.get(splitSymbol)
            if holding.Invested:
                Main.log(" Found split===================")
                splitType = {0: "Warning", 1: "SplitOccurred"}.get(split.Type)
                Main.log(
                    f"{self.main.Time} >> SPLIT >> {splitType} - {split.Symbol} -"
                    f" {split.SplitFactor} - {self.main.Portfolio.Cash} - {self.main.Portfolio[split.Symbol].Price}")

                Main.log(" split - cancelling symbol orders " + str(split.Symbol))
                tag: Tag = Tag(AlgoKey.COMMON, SourceKey.COMMON, " Cancelling all symbol orders "
                               + str(split.Symbol.Value)
                               + " because of split")
                self.stateManager.cancelSymbolOrders(split.Symbol, tag)
                Main.log(" split - liquidating symbol " + str(split.Symbol))
                self.main.Liquidate(split.Symbol, tag=Tag(AlgoKey.COMMON, SourceKey.COMMON,
                                                          "Split liquidate " + str(split.Symbol.Value)).toStr())

                self.securityChanger.resetSymbolIndicators(split.Symbol)


                Main.log(" split - did all symbolstates[symbol]  quantitys get set to 0 from liquidate?")

                #self.stateManager.factorStateQuantitys(split.Symbol, split.SplitFactor)

                '''
    
                    self.slow.Reset()
                    self.fast.Reset()
                    self.faster.Reset()
                    self.main.WarmUpIndicator(self.symbol, self.slow)
                    self.main.WarmUpIndicator(self.symbol, self.fast)
                    self.main.WarmUpIndicator(self.symbol, self.faster)
                '''

