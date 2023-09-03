
from frameworkAlgo.state.keys import AlgoKey, SourceKey


class Tag:
    def __init__(self, algoKey: AlgoKey, sourceKey: SourceKey, description: str):
        self.algoKey: AlgoKey = algoKey
        self.sourceKey: SourceKey = sourceKey
        self.description: str = description


    @staticmethod
    def fromStr(tag: str):
        tagSplit: [] = tag.split(",")
        return Tag(AlgoKey.from_str(tagSplit[0]), SourceKey.from_str(tagSplit[1]), tagSplit[2])

    # Self: https://stackoverflow.com/questions/70887626/python-type-hinting-a-classmethod-that-returns-an-instance-of-the-class-for-a
    def toStr(self) -> str:
        tagStr = ",".join([self.algoKey.value, self.sourceKey.value, str(self.description)])
        return tagStr
