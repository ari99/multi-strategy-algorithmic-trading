import QuantConnect
from QuantConnect.Algorithm.Framework.Alphas import Insight

from AlgorithmImports import *

from frameworkAlgo.state.tagModule import Tag


class TaggedInsight(Insight):
    def __init__(self,  tag: Tag, symbol: Union[QuantConnect.Symbol, str], period: any,
                 type: QuantConnect.Algorithm.Framework.Alphas.InsightType,
                 direction: QuantConnect.Algorithm.Framework.Alphas.InsightDirection,
                 magnitude: Optional[float] = None, confidence: Optional[float] = None,
                 sourceModel: str = None, weight: Optional[float] = None) -> None:
        super().__init__(symbol, period, type, direction, magnitude, confidence, sourceModel, weight)
        self.tag: Tag = tag
