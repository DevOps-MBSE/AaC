from tkinter import Tk, TOP, NW, Label, Canvas, Entry, RIGHT
from tkinter.ttk import Notebook, Frame

VIEWS_FRAME = None
IS_DIAGRAM_VIEW = True


def get_model_views(root_window: Tk, view_width: int, view_height: int) -> callable:
    """
    Creates a view ....

    Args:
        root_window: The window to attach the models tree frame to
        view_width (int): The width of the canvas

    Returns:
        A callback function for updating the model view between diagram and text.
    """
    tab_view_frame = Frame(root_window, width=view_width, height=view_height)
    tab_view_frame.pack(fill='both', expand=True, side=RIGHT)

    global VIEWS_FRAME
    global IS_DIAGRAM_VIEW
    VIEWS_FRAME = tab_view_frame

    set_diagram_view_frame(tab_view_frame, IS_DIAGRAM_VIEW, view_width, view_height)

    return _switch_views


def set_diagram_view_frame(root_frame: Frame, is_diagram_view: bool, view_width: int, view_height: int):
    print(view_width, view_height)

    if (is_diagram_view):
        view_diagram_notebook(root_frame, view_width, view_height)
    else:
        view_model_text(root_frame, view_width, view_height)


def view_diagram_notebook(window_frame: Frame, view_width: int, view_height: int):
    tabs_notebook = Notebook(window_frame, height=view_width, width=view_height)

    diagram_tab = _get_diagram_tab_frame(tabs_notebook, view_width, view_height)
    properties_tab = _get_properties_tab_frame(tabs_notebook, view_width, view_height)
    imports_tab = _get_imports_tab_frame(tabs_notebook, view_width, view_height)

    _add_tab_to_notebook(tabs_notebook, diagram_tab, {"text": "Diagram"})
    _add_tab_to_notebook(tabs_notebook, properties_tab, {"text": "Properties"})
    _add_tab_to_notebook(tabs_notebook, imports_tab, {"text": "Imports"})

    tabs_notebook.pack(fill='both', expand=True)


def view_model_text(window_frame: Frame, view_width: int, view_height: int):
    canvas = Canvas(window_frame, bg="yellow", height=view_width, width=view_height)
    canvas.pack(fill='both', expand=True)


def _add_tab_to_notebook(root_notebook: Notebook, tab_to_add: Frame, frame_kwargs):
    root_notebook.add(tab_to_add, **frame_kwargs)


def _get_diagram_tab_frame(root_notebook: Notebook, width: int, height: int) -> Frame:
    diagram_frame = Frame(root_notebook, width=width, height=height)
    diagram_frame.place()

    Label(diagram_frame, text="test").pack()

    return diagram_frame


def _get_properties_tab_frame(root_notebook: Notebook, width: int, height: int) -> Frame:
    properties_frame = Frame(root_notebook)
    return properties_frame


def _get_imports_tab_frame(root_notebook: Notebook, width: int, height: int) -> Frame:
    imports_frame = Frame(root_notebook)
    return imports_frame


def _switch_views():
    global VIEWS_FRAME
    global IS_DIAGRAM_VIEW

    # Clear existing frames
    for widgets in VIEWS_FRAME.winfo_children():
        widgets.destroy()

    IS_DIAGRAM_VIEW = (not IS_DIAGRAM_VIEW)

    set_diagram_view_frame(VIEWS_FRAME, IS_DIAGRAM_VIEW, VIEWS_FRAME.winfo_width(), VIEWS_FRAME.winfo_height())

