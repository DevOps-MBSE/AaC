from attr import attrs, attrib
from tkinter import (
    Text,
    Frame,
    Canvas,
    Label,
    LEFT,
    END,
    TOP,
)

from aac.ui.components.BaseTkinterComponent import BaseTkinterComponent


@attrs
class ColoredCircle(BaseTkinterComponent):
    """
    Component class for a colored circle on a canvas widget.

    Attributes:
        parent_widget (Widget): inherited attribute - the parent Tkinter widget
        circle_color (str): a string representing the circle's color. Must be hexadecimal
                                or one of the following ("white", "black", "red", "green",
                                "blue", "cyan", "yellow", and "magenta")
        circle_radius (int): The radius of the circle, defaults to '30'

    Returns:
        A frame with a canvas and colored circle.
    """

    circle_color = attrib(default="black")
    circle_radius = attrib(default=30)

    def build(self):
        frame = Frame(self.parent_widget, bg="yellow")
        frame.pack(side=TOP, pady=10)

        x1 = 0
        y1 = 0
        x2 = x1 + self.circle_radius
        y2 = y1 + self.circle_radius

        circle_canvas = Canvas(frame, height=self.circle_radius, width=self.circle_radius)
        circle_canvas.create_oval(x1, y1, x2, y2, fill=self.circle_color, outline="#DDD", width=4)
        circle_canvas.pack()

        return frame
