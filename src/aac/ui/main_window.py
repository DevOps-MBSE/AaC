from tkinter import Tk

from aac.ui.menu_bar import menu_bar
from aac.ui.models_tree import add_models_tree
from aac.ui.model_views import get_model_views
from aac.ui.view_diagram_button import add_view_diagram_button


def main_window() -> None:
    """Runs the main AaC UI window."""

    def toggle_view_diagram() -> None:
        print("boop")
        view_toggle_callback()

    main_window = Tk()
    main_window.title("Architecture-as-Code")

    main_window_width = main_window.winfo_screenwidth()
    main_window_height = main_window.winfo_screenheight()

    main_window.geometry("%dx%d" % (main_window_width, main_window_height))
    main_window_menu_bar = menu_bar(main_window)
    main_window.config(menu=main_window_menu_bar)

    # Calculate main_window widget widths and heights
    model_tree_view_width = 200
    model_tree_view_height = main_window_height

    models_view_width = main_window_width - model_tree_view_width
    models_view_height = main_window_height

    view_diagram_button_width = main_window_width
    view_diagram_button_height = 30

    # Add main_window widgets
    add_models_tree(main_window, model_tree_view_width, model_tree_view_height)
    add_view_diagram_button(main_window, toggle_view_diagram, view_diagram_button_width, view_diagram_button_height)

    view_toggle_callback = get_model_views(main_window, models_view_width, models_view_height)

    return main_window

