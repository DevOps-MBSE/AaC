from tkinter import Tk

from aac.ui.menu_bar import menu_bar
from aac.ui.models_tree import add_models_tree
from aac.ui.model_views import add_model_views
from aac.ui.view_diagram_button import add_view_diagram_button


def main_window() -> None:
    """Runs the main AaC UI window."""
    main_window = Tk()
    main_window.title("Architecture-as-Code")

    width, height = _get_window_dimensions(main_window)
    main_window.geometry("%dx%d" % (width, height))
    main_window_menu_bar = menu_bar(main_window)
    main_window.config(menu=main_window_menu_bar)

    model_tree_view_width = 200
    tabs_view_width = main_window.winfo_screenwidth() - model_tree_view_width

    add_models_tree(main_window, model_tree_view_width)
    add_model_views(main_window, tabs_view_width)
    add_view_diagram_button(main_window)

    return main_window


def _get_window_dimensions(window) -> tuple[int, int]:
    """
    Gets the window width and height and returns them in a tuple.

    Returns
        Tuple of window width and window height
    """
    return (window.winfo_screenwidth(), window.winfo_screenheight())
