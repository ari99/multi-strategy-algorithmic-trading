
from AlgorithmImports import *

from frameworkAlgo.algo import Algo
from frameworkAlgo.mainHolder import Main
from frameworkAlgo.common.positionChange import PositionChange
from frameworkAlgo.common.positionChangeCreator import PositionChangeCreator
from frameworkAlgo.ltm.taggedPortfolioTarget import TaggedPortfolioTarget
from frameworkAlgo.state.keys import AlgoKey
from frameworkAlgo.state.stateManager import StateManager


class TargetCombiner:
    def __init__(self, main: QCAlgorithm, algos: List[Algo], stateManager: StateManager) -> None:
        self.main = main
        self.algos: List[Algo] = algos
        self.stateManager: StateManager = stateManager

    def createTargets(self, insights: List[Insight]) -> List[PortfolioTarget]:

        allTargets: List[PortfolioTarget] = []
        portfolioTargets: List[PortfolioTarget] = self.algos[0].getPortfolioConstruction().CreateTargets(self.main, insights)

        allRiskTargets:  List[PortfolioTarget] = []
        for algo in self.algos:
            riskManagement: IRiskManagementModel = algo.getRiskManagement()
            riskTargets: List[PortfolioTarget] = riskManagement.ManageRisk(self.main, portfolioTargets)
            allRiskTargets.extend(riskTargets)

        algoTargets: List[PortfolioTarget] = self.combineTargets(portfolioTargets, allRiskTargets)
        for target in algoTargets:
            allTargets.append(target)

        return allTargets

    def combineTargets(self, portfolioTargets: List[TaggedPortfolioTarget], riskTargets: List[TaggedPortfolioTarget]):
        combinedTargets: List[TaggedPortfolioTarget] = []
        for portfolioTarget in portfolioTargets:
            portfolioTargetSymbol: Symbol = portfolioTarget.Symbol
            algoKey: AlgoKey = portfolioTarget.tag.algoKey
            change: PositionChange = PositionChangeCreator.createTargetChange(portfolioTarget)

            addPortfolioTarget: bool = True
            if len(riskTargets) > 0:
                for index,riskTarget in enumerate(riskTargets):
                    if portfolioTargetSymbol == riskTarget.Symbol:
                        if change.isReversePositionSymbolAlgo:
                            riskTargets.pop(index)
                        else: # if there is a risk target and the portfolio target is not a reversal, just add the risk target
                            addPortfolioTarget = False

            if addPortfolioTarget:
                if change.isReversePositionSymbolAlgo or change.isDecreasePositionSymbolAlgo or change.isLiquidateSymbolAlgo:
                    self.stateManager.cancelSymbolAlgoOrders(portfolioTargetSymbol, algoKey,
                                                         " new reversal portfolio target for "
                                                         + str(portfolioTargetSymbol.Value) + " algo " + str(algoKey))
                combinedTargets.append(portfolioTarget)

        # add any risk targets that werent in portfolioTargets
        appendendSymbolAlgoKeys: Dict[Symbol, List[AlgoKey]]= {}
        for riskTarget in riskTargets:
            algoKey: AlgoKey = riskTarget.tag.algoKey
            symbol: Symbol = riskTarget.Symbol
            if symbol in appendendSymbolAlgoKeys and \
                algoKey in appendendSymbolAlgoKeys[symbol]:
                Main.log("Not adding risk target because already have one for this algo : "
                                + riskTarget.tag.toStr())
            else:
                self.stateManager.cancelSymbolAlgoOrders(symbol, algoKey,
                                                     " new risk target for " + str(symbol.Value)
                                                         + " algo " + str(algoKey))
                combinedTargets.append(riskTarget)
                if symbol in appendendSymbolAlgoKeys:
                    appendendSymbolAlgoKeys[symbol].append(algoKey)
                else:
                    appendendSymbolAlgoKeys[symbol] = [algoKey]

        self.debugResults(combinedTargets)
        return combinedTargets


    def debugResults(self, targets: List[TaggedPortfolioTarget]):
        if len(targets) > 0:
            Main.log(" All targets in target combiner: " + str(len(targets)))
            for target in targets:
                Main.log("Target: " + str(target.tag.toStr()))
