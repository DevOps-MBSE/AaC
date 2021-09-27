from abc import ABC, abstractmethod

class Model(ABC):

    @abstractmethod
    def getSubModels():
        pass

    def getBehaviors():
        pass