from abc import ABC, abstractmethod


class DesignDocumentGenerator(ABC):
    @abstractmethod
    def make_section(self, title: str, level: int, text: str) -> str:
        raise NotImplementedError("Implement me!")

    @abstractmethod
    def make_heading(self, title: str, level: int) -> str:
        raise NotImplementedError("Implement me!")
