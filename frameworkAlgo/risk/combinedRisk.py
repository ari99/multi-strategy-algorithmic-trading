
from AlgorithmImports import *

from frameworkAlgo.ltm.taggedPortfolioTarget import TaggedPortfolioTarget

class CombinedRisk(RiskManagementModel):

    def __init__(self, risks: List[RiskManagementModel]):
        super().__init__()
        self.risks = risks

    def ManageRisk(self, algorithm: QCAlgorithm, targets: List[PortfolioTarget])-> List[TaggedPortfolioTarget]:
        allRiskAdjustedTargets: List[TaggedPortfolioTarget] = list()
        for risk in self.risks:
            riskTargets: List[TaggedPortfolioTarget] = risk.ManageRisk(algorithm,targets)
            for target in riskTargets:
                # TODO remove targets for duplicate symbols
                allRiskAdjustedTargets.append(target)
        return allRiskAdjustedTargets