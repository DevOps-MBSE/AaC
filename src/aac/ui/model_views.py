from tkinter import Tk, TOP, NW
from tkinter.ttk import Notebook, Frame, Style


def add_model_views(root_window: Tk, view_width: int) -> None:
    """
    Creates a view ....

    Args:
        root_window: The window to attach the models tree frame to
        view_width (int): The width of the canvas
    """
    tab_view_frame = Frame(root_window, width=view_width, height=root_window.winfo_screenheight(), borderwidth=1)
    tab_view_frame.pack(side=TOP, anchor=NW)

    tabs_notebook = Notebook(tab_view_frame)

    diagram_tab = Frame(tabs_notebook)
    properties_tab = Frame(tabs_notebook)
    imports_tab = Frame(tabs_notebook)

    _add_tab_to_notebook(tabs_notebook, diagram_tab, {"text": "Diagram"})
    _add_tab_to_notebook(tabs_notebook, properties_tab, {"text": "Properties"})
    _add_tab_to_notebook(tabs_notebook, imports_tab, {"text": "Imports"})

    tabs_notebook.pack()


def _add_tab_to_notebook(root_notebook: Notebook, tab_to_add: Frame, frame_kwargs):
    root_notebook.add(tab_to_add, **frame_kwargs)
