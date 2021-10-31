from abc import ABC, abstractmethod


class DesignDocumentGenerator(ABC):
    @abstractmethod
    def make_heading(title: str, level: int) -> str:
        raise NotImplementedError("Implement me!")
