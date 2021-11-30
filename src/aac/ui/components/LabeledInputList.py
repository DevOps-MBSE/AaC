"""Python Tkinter reusable component for a list of items that the user can manipulate."""
from attr import attrs, attrib, validators
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

    Attributes:
        listbox_content (list[str]): a list of strings that will compose the list of entries
        listbox_label_text (str): The listbox label for the list of items
        input_content (str): An initial input box value
        input_label_text (str): The text for the input box label
    """

    listbox_content = attrib(default=[], validator=validators.instance_of(list))
    listbox_label_text = attrib(default="label", validator=validators.instance_of(str))

    input_content = attrib(default="", validator=validators.instance_of(str))
    input_label_text = attrib(default="label", validator=validators.instance_of(str))

    def build(self):
        """
        Create the component, pack the tkinter widget, and return the encompassing frame.

        Returns:
            A packed tkinter.Frame containing the component's content.
        """
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
