import math

from AlgorithmImports import *

from frameworkAlgo.mainHolder import Main
from frameworkAlgo.ltm.taggedPortfolioTarget import TaggedPortfolioTarget
from frameworkAlgo.state.stateManager import StateManager
from frameworkAlgo.state.states import SymbolAlgoState, SymbolState


class TaggedImmediateExecution(ExecutionModel):
    '''Provides an implementation of IExecutionModel that immediately
        submits market orders to achieve the desired portfolio targets'''

    def __init__(self, stateManager: StateManager):
        '''Initializes a new instance of the ImmediateExecutionModel class'''
        self.targetsCollection = PortfolioTargetCollection()
        self.stateManager = stateManager

    def Execute(self, algorithm, targets: List[TaggedPortfolioTarget]):
        '''
            Immediately submits orders for the specified portfolio targets.
            Args:
                algorithm: The algorithm instance
                targets: The portfolio targets to be ordered
        '''

        # for performance we check count value, OrderByMarginImpact and ClearFulfilled are expensive to call
        seenTargets: List[str] = []
        benchmark = Symbol.Create("SPY", SecurityType.Equity, Market.USA)

        if len(targets) > 0:
            Main.log("targets is not empty")
            target: TaggedPortfolioTarget
            for target in targets:

                targetKey: str = str(target.tag.algoKey)+"_"+str(target.Symbol)
                if targetKey in seenTargets or target.Symbol == benchmark:
                    continue
                else:
                    seenTargets.append(targetKey)


                Main.log("---Immediate exectution - " + str(algorithm.Time) + " with target quantity "
                             + str(target.Quantity) + " " + str(target.Symbol), symbol=target.Symbol)
                security = algorithm.Securities[target.Symbol]
                # calculate remaining quantity to be ordered
                # GetUnorderedQuantity always sets percentage quantities to 0
                # quantity = OrderSizing.GetUnorderedQuantity(algorithm, target, security)
                #algorithm.Debug("after  GetUnorderedQuantity quantity " + str(quantity) + " " + str(target.Symbol))
                quantity = target.Quantity
                # checking for quantity 0 only makes sense with marketorder
                #if quantity != 0:

                symbolAlgoState: SymbolAlgoState = self.stateManager.getSymbolAlgoStateOrDefault(target.Symbol,
                                                                                                 target.tag.algoKey)
                symbolState: SymbolState = self.stateManager.getSymbolStateOrDefault(target.Symbol)
                aboveMinimumPortfolio = BuyingPowerModelExtensions.\
                    AboveMinimumOrderMarginPortfolioPercentage(security.BuyingPowerModel, security,
                                                               quantity, algorithm.Portfolio,
                                                               algorithm.Settings.MinimumOrderMarginPortfolioPercentage)
                if (aboveMinimumPortfolio
                        and (not symbolState.isInvested or # if another strat is invested in the symbol, dont invest
                    (symbolState.isInvested and symbolAlgoState.isInvested))
                    and not symbolState.orderExecutedButNotFilled
                    and not symbolAlgoState.orderExecutedButNotFilled
                    ):  # allow reversal for same strat
                        # use SetHoldings when dealing with percentages. If you already hold the equity
                        # in the opposite direction SetHoldings will place an order for extra quantity to cover the oppisite
                        # direction quantity and still meet the target percentage

                        # next need to keep track of quantities for the last order for each algo
                        # and sell the algos quantities instead of liquidate all
                        # also setholdings wont add to an existing position
                        # figure out how to do a limit insight here too
                        # algorithm.SetHoldings(target.Symbol, target.Quantity, tag=target.tag.toStr())
                        # algorithm.StopMarketOrder(target.Symbol,
                        #                         -self.Portfolio[self.spy].Quantity, data[self.spy].Close * 0.7)
                        # MarketOrder does not liquidate the previous holdings
                        orderQuantity = target.Quantity


                        symbolAlgoState.orderExecutedButNotFilled=True # TODO set on liquidates in other parts of the code?
                        symbolState.orderExecutedButNotFilled=True
                        self.stateManager.setSymbolAlgoState(symbolAlgoState)
                        self.stateManager.setSymbolState(symbolState)
                        orderQuantity = math.floor(orderQuantity)
                        algorithm.MarketOrder(target.Symbol, orderQuantity, tag=target.tag.toStr())
                else:
                    Main.log("Not above min " + str(algorithm.Settings.MinimumOrderMarginPortfolioPercentage))


            self.targetsCollection.ClearFulfilled(algorithm)