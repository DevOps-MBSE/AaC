from abc import ABC, abstractmethod


class DesignDocumentGenerator(ABC):
    @abstractmethod
    def make_document_outline(self, model: dict) -> str:
        raise NotImplementedError("Implement me!")

    @abstractmethod
    def make_section(self, title: str, level: int, text: str) -> str:
        raise NotImplementedError("Implement me!")

    @abstractmethod
    def make_heading(self, title: str, level: int) -> str:
        raise NotImplementedError("Implement me!")

    @abstractmethod
    def make_link(self, text: str, url: str) -> str:
        raise NotImplementedError("Implement me!")

    @abstractmethod
    def make_ordered_list(self, items: list[str]) -> str:
        raise NotImplementedError("Implement me!")

    @abstractmethod
    def make_unordered_list(self, items: list[str]) -> str:
        raise NotImplementedError("Implement me!")

    @abstractmethod
    def make_code_line(self, code: str) -> str:
        raise NotImplementedError("Implement me!")

    @abstractmethod
    def make_code_block(self, code: str, language: str) -> str:
        raise NotImplementedError("Implement me!")
