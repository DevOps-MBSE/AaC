from tkinter import Tk, PanedWindow, LEFT, Listbox
from tkinter.ttk import Treeview

from aac.ui.menu_bar import menu_bar
from aac.ui.models_tree import add_models_tree
from aac.ui.model_views import add_model_views


def main_window() -> None:
    """Runs the main AaC UI window."""

    def toggle_view_diagram() -> None:
        print("boop")
        view_toggle_callback()

    root_window = Tk()
    root_window.title("Architecture-as-Code")

    main_window_width = root_window.winfo_screenwidth()
    main_window_height = root_window.winfo_screenheight()

    root_window.geometry("%dx%d" % (main_window_width, main_window_height))
    root_window_menu_bar = menu_bar(root_window)
    root_window.config(menu=root_window_menu_bar)

    main_window = PanedWindow(showhandle=True)

    # Calculate main_window widget widths and heights
    model_tree_view_width = 200
    model_tree_view_height = main_window_height

    print(f"model_tree_view width x height: {model_tree_view_width}, {model_tree_view_height}")

    view_diagram_button_width = main_window_width - model_tree_view_width
    view_diagram_button_height = 30

    print(f"view_diagram_button width x height: {view_diagram_button_width}, {view_diagram_button_height}")

    models_view_width = main_window_width - model_tree_view_width
    models_view_height = main_window_height

    print(f"models_view width x height: {models_view_width}, {models_view_height}")

    # Add main_window widgets
    add_models_tree(main_window)
    add_model_views(main_window)

    main_window.pack(fill="both", expand=True)

    return root_window

