from attr import attrs, attrib
from tkinter import (
    Listbox,
    Frame,
    Label,
    END,
    TOP,
    BOTTOM,
    RIDGE,
)

from aac.ui.components.BaseTkinterComponent import BaseTkinterComponent


@attrs
class LabeledInputList(BaseTkinterComponent):
    """
    Component class for a labeled list box.

    Returns:
        A frame with a label and listbox.
    """

    listbox_content = attrib()
    label_text = attrib()

    def build(self):
        frame = Frame(self.parent_widget)
        frame.pack(side=BOTTOM, fill="x", expand=True, pady=10)

        listbox_frame = Frame(self.parent_widget, borderwidth=3, relief=RIDGE)
        listbox_frame.pack(side=BOTTOM, fill="x", expand=True)

        listbox_frame_label = Label(listbox_frame, text=self.label_text)
        listbox_frame_label.pack(side=TOP)

        listbox = Listbox(listbox_frame)

        for entry in self.listbox_content:
            listbox.insert(END, entry)

        listbox.pack(side=BOTTOM, fill="x", expand=True)

        return frame
