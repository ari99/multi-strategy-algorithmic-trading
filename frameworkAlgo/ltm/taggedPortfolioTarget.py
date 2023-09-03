import typing

import QuantConnect
from QuantConnect.Algorithm.Framework.Portfolio import PortfolioTarget

from frameworkAlgo.state.tagModule import Tag


class TaggedPortfolioTarget(PortfolioTarget):
    def __init__(self, tag: Tag,
                 symbol: typing.Union[QuantConnect.Symbol, str],
                 quantity: float) -> None:
        super().__init__(symbol, quantity)
        self.tag: Tag = tag


