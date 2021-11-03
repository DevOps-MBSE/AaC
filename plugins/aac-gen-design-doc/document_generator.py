"""Basic Design Document generation interface."""
import os
from abc import ABC, abstractmethod

from jinja2 import Environment, FileSystemLoader


class DesignDocumentGenerator(ABC):
    """A generic Design Document generation class."""

    def load_templates(self) -> list:
        """Load all plugin templates."""
        env = Environment(
            loader=FileSystemLoader(f"{os.path.dirname(__file__)}/templates/"),
            autoescape=True,
        )
        return [env.get_template(name) for name in env.list_templates()]

    def generate_templates(self, templates: list, properties: dict) -> dict:
        """Generate all plugin templates."""
        generated_templates = {}

        def generate_template(template, properties):
            name = template.name.replace(".jinja2", "")
            generated_templates[name] = template.render(properties)

        [generate_template(template, properties) for template in templates]
        return generated_templates

    @abstractmethod
    def make_document_outline(self, model: dict) -> str:
        """Return a document outline."""
        raise NotImplementedError("Implement me!")

    @abstractmethod
    def make_section(self, title: str, level: int, text: str) -> str:
        """Return a document section."""
        raise NotImplementedError("Implement me!")

    @abstractmethod
    def make_heading(self, title: str, level: int) -> str:
        """Return a document heading."""
        raise NotImplementedError("Implement me!")
