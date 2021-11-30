from attr import attrs, attrib
from tkinter import (
    Text,
    Frame,
    Label,
    LEFT,
    END,
    TOP,
)

from aac.ui.components.BaseTkinterComponent import BaseTkinterComponent


@attrs
class LabeledInput(BaseTkinterComponent):
    """
    Component class for labeled text input.

    Attributes:
        parent_widget (Widget): inherited attribute - the parent Tkinter widget
        label_text (str):
        input_value (str):

    Returns:
        A frame with a label and text input.
    """

    label_text = attrib()
    input_value = attrib()

    def build(self):
        """
        Create the component, pack the tkinter widget, and return the encompassing frame.

        Returns:
            A packed tkinter.Frame containing the component's content.
        """
        frame = Frame(self.parent_widget)
        frame.pack(side=TOP, fill="x", expand=True, pady=10)

        properties_components_label = Label(frame, text=self.label_text)
        properties_components_label.pack(side=LEFT, padx=(0, 20))

        text = Text(frame, height=1)
        text.insert(END, self.input_value)
        text.pack(side=LEFT, fill="x", expand=True)
        return frame
