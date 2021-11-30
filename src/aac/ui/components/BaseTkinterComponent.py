"""Base Python Tkinter reusable component class. Serves only as an abstract base class."""
from attr import attrs, attrib, validators

from tkinter import Widget


@attrs
class BaseTkinterComponent:
    """
    Base class for all custom Tkinter components. DO NOT USE.

    Attributes:
        parent_widget (tkinter.Widget): The parent widget to attach the component to.
    """

    parent_widget = attrib(type=Widget, validator=validators.instance_of(Widget))

    def build(self):
        """
        Create the component, pack the tkinter widget, and return the encompassing frame.

        Returns:
            A packed tkinter.Frame containing the component's content.
        """
        raise NotImplementedError()
