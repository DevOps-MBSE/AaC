from tkinter import Tk, TOP, NW
from tkinter.ttk import Notebook, Frame, Style


def add_tab_views(root_window: Tk, view_width: int) -> None:
    """
    Creates a view ....

    Args:
        root_window: The window to attach the models tree frame to
        view_width (int): The width of the canvas
    """
    style = Style()
    style.configure('My.TFrame', background='green')

    tab_view_frame = Frame(root_window, width=view_width, height=root_window.winfo_screenheight(), style='My.TFrame')
    tab_view_frame.pack(side=TOP, anchor=NW)

    tabs_notebook = Notebook(tab_view_frame)

    tab1 = Frame(tabs_notebook)
    tab2 = Frame(tabs_notebook)
    tab3 = Frame(tabs_notebook)

    _add_tab_to_notebook(tabs_notebook, tab1, {"text": "Notebook tab1"})
    _add_tab_to_notebook(tabs_notebook, tab2, {"text": "Notebook tab2"})
    _add_tab_to_notebook(tabs_notebook, tab3, {"text": "Notebook tab3"})

    tabs_notebook.pack()


def _add_tab_to_notebook(root_notebook: Notebook, tab_to_add: Frame, frame_kwargs):
    root_notebook.add(tab_to_add, **frame_kwargs)
