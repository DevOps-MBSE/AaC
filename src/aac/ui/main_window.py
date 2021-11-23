from tkinter import Tk, PanedWindow

from aac.ui.menu_bar import menu_bar
from aac.ui.models_treeview import add_models_treeview
from aac.ui.model_views import add_model_views


def main_window() -> None:
    """Runs the main AaC UI window."""

    root_window = Tk()
    root_window.title("Architecture-as-Code")

    main_window_width = root_window.winfo_screenwidth()
    main_window_height = root_window.winfo_screenheight()

    root_window.geometry("%dx%d" % (main_window_width, main_window_height))
    root_window_menu_bar = menu_bar(root_window)
    root_window.config(menu=root_window_menu_bar)

    main_window = PanedWindow(showhandle=True)
    main_window.pack(fill="both", expand=True)

    # Add main_window widgets
    add_models_treeview(main_window)
    add_model_views(main_window)

    return root_window
