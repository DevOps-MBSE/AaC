from tkinter import Tk, Button, BOTTOM, SE, Label, LEFT, RIGHT
from tkinter.ttk import Style, Frame


def add_view_diagram_button(parent_window: Tk, button_callback: callable, view_width: int, view_height: int) -> None:
    """
    ...
    """
    CONST_ON_TEXT_VALUE = "On"
    CONST_OFF_TEXT_VALUE = "Off"

    def _toggle(toggle_value=[0]):
        """
        a list default argument has a fixed address
        """

        toggle_value[0] = not toggle_value[0]
        if toggle_value[0]:
            view_diagram_button.config(text=CONST_OFF_TEXT_VALUE, background=state_color_dict[CONST_OFF_TEXT_VALUE], activebackground=state_color_dict[CONST_OFF_TEXT_VALUE])
        else:
            view_diagram_button.config(text=CONST_ON_TEXT_VALUE, background=state_color_dict[CONST_ON_TEXT_VALUE], activebackground=state_color_dict[CONST_ON_TEXT_VALUE])

        button_callback()

    state_color_dict = {
        CONST_ON_TEXT_VALUE: 'green',
        CONST_OFF_TEXT_VALUE: 'red',
    }

    toggle_view_frame = Frame(parent_window, width=view_width, height=view_height)
    toggle_view_frame.pack(side=BOTTOM, anchor=SE, fill='both', expand=True)

    view_diagram_button = Button(toggle_view_frame, text=CONST_ON_TEXT_VALUE, bd=0, command=_toggle, width=3, height=2)
    view_diagram_button.config(text=CONST_ON_TEXT_VALUE, background=state_color_dict[CONST_ON_TEXT_VALUE], activebackground=state_color_dict[CONST_ON_TEXT_VALUE])  # Set Default State and Style

    view_diagram_button.pack(side=RIGHT, fill='both')

    label = Label(toggle_view_frame, text="View Diagram")
    label.pack(side=RIGHT)

    parent_window.add(toggle_view_frame)

