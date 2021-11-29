from attr import attrs, attrib
from tkinter import (
    font,
    PanedWindow,
    Canvas,
    Text,
    Button,
    Listbox,
    Frame,
    Label,
    LEFT,
    RIGHT,
    CENTER,
    END,
    TOP,
    BOTTOM,
    RIDGE,
)
from tkinter.font import BOLD

from aac.ui.components.BaseTkinterComponent import BaseTkinterComponent
from aac.ui.components.LabeledInput import LabeledInput


@attrs
class InsertNewItemInput(LabeledInput):
    """
    Component class for a labeled input used to insert new items.

    Returns:
        A frame with a label and text input.
    """

    button_command_callable = attrib()

    def build(self):
        frame = LabeledInput.build(self)

        plus_button_font = font.Font(size=11, weight=BOLD)
        plus_button = Button(
            frame, text="+", command=self.button_command_callable, font=plus_button_font
        )
        plus_button.pack(side=RIGHT, padx=(20, 0))

        return frame
