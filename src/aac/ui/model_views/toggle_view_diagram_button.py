"""Provides the button to toggle between the available model views."""
from tkinter import Tk, Button, BOTTOM, Label, RIGHT, Frame


def get_view_diagram_button(parent_window: Tk, button_callback: callable) -> None:
    """
    Provides a frame containing the toggle button for switching between model views.
    """
    CONST_ON_TEXT_VALUE = "On"
    CONST_OFF_TEXT_VALUE = "Off"

    def config_button(view_diagram_button: Button, text_value: str):
        """Configures the toggle button's text and color."""
        view_diagram_button.config(
            text=text_value,
            background=state_color_dict[text_value],
            activebackground=state_color_dict[text_value],
        )

    def toggle_view(toggle_value=[0]):
        """The function executed when the button is pressed; toggles between and on and off state and executes the button_callback callable."""

        toggle_value[0] = not toggle_value[0]
        if toggle_value[0]:
            config_button(view_diagram_button, CONST_OFF_TEXT_VALUE)
        else:
            config_button(view_diagram_button, CONST_ON_TEXT_VALUE)

        button_callback()

    state_color_dict = {
        CONST_ON_TEXT_VALUE: "green",
        CONST_OFF_TEXT_VALUE: "red",
    }

    toggle_view_frame = Frame(parent_window, height=40)

    view_diagram_button = Button(
        toggle_view_frame, text=CONST_ON_TEXT_VALUE, bd=1, command=toggle_view
    )
    config_button(view_diagram_button, CONST_ON_TEXT_VALUE)

    view_diagram_button.pack(side=RIGHT)

    label = Label(toggle_view_frame, text="View Diagram")
    label.pack(side=RIGHT)

    toggle_view_frame.pack(side=BOTTOM)

    return toggle_view_frame
