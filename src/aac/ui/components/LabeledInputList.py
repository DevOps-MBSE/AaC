from attr import attrs, attrib
from tkinter import (
    font,
    Button,
    Listbox,
    Frame,
    Label,
    RIGHT,
    END,
    TOP,
    BOTTOM,
    RIDGE,
)

from aac.ui.components.BaseTkinterComponent import BaseTkinterComponent
from aac.ui.components.LabeledInput import LabeledInput


@attrs
class LabeledInputList(BaseTkinterComponent):
    """
    Component class for a labeled user-input list.

    Returns:
        A frame with a label and listbox.
    """

    listbox_content = attrib()
    listbox_label_text = attrib()

    input_content = attrib()
    input_label_text = attrib()

    def build(self):
        labeled_input_list_frame = Frame(self.parent_widget)
        labeled_input_list_frame.pack(side=TOP, fill="x", expand=True, pady=10)

        # Labeled Input #
        labeled_input_frame = LabeledInput(labeled_input_list_frame, self.input_label_text, self.input_content).build()

        # Add Entry Button for Labeled Input #
        plus_button_font = font.Font(size=11, weight=font.BOLD)
        plus_button = Button(
            labeled_input_frame, text="+", command=do_nothing, font=plus_button_font
        )
        plus_button.pack(side=RIGHT, padx=(20, 0))

        # List of current values #
        listbox_frame = Frame(self.parent_widget, borderwidth=3, relief=RIDGE)
        listbox_frame.pack(side=BOTTOM, fill="x", expand=True)

        listbox_frame_label = Label(listbox_frame, text=self.listbox_label_text)
        listbox_frame_label.pack(side=TOP)

        listbox = Listbox(listbox_frame)

        for entry in self.listbox_content:
            listbox.insert(END, entry)

        listbox.pack(side=BOTTOM, fill="x", expand=True)

        return labeled_input_list_frame


def do_nothing():
    print("Do nothing")
