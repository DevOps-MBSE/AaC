from tkinter import Tk, Button, BOTTOM, SE, Label, LEFT, RIGHT
from tkinter.ttk import Style, Frame

CONST_ON_TEXT_VALUE = "On"
CONST_OFF_TEXT_VALUE = "Off"


def add_view_diagram_button(root_window: Tk) -> None:
    """
    ...
    """

    def _toggle(toggle_value=[0]):
        """
        a list default argument has a fixed address
        """

        toggle_value[0] = not toggle_value[0]
        if toggle_value[0]:
            view_diagram_button.config(text=CONST_OFF_TEXT_VALUE, background=state_color_dict[CONST_OFF_TEXT_VALUE], activebackground=state_color_dict[CONST_OFF_TEXT_VALUE])
        else:
            view_diagram_button.config(text=CONST_ON_TEXT_VALUE, background=state_color_dict[CONST_ON_TEXT_VALUE], activebackground=state_color_dict[CONST_ON_TEXT_VALUE])

    state_color_dict = {
        CONST_ON_TEXT_VALUE: 'green',
        CONST_OFF_TEXT_VALUE: 'red',
    }

    style = Style()
    style.configure('toggle_view_frame_on.TFrame', width=80)

    toggle_view_frame = Frame(root_window, style='toggle_view_frame.TFrame')
    toggle_view_frame.pack(side=BOTTOM, anchor=SE)

    label = Label(toggle_view_frame, text="View Diagram")
    label.pack(side=LEFT)

    view_diagram_button = Button(toggle_view_frame, text=CONST_ON_TEXT_VALUE, bd=0, command=_toggle)
    view_diagram_button.config(text=CONST_ON_TEXT_VALUE, background=state_color_dict[CONST_ON_TEXT_VALUE], activebackground=state_color_dict[CONST_ON_TEXT_VALUE])  # Set Default State and Style

    view_diagram_button.pack(side=RIGHT)
