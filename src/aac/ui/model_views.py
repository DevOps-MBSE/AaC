from tkinter import Tk, TOP, NW, Label, Canvas, Entry, RIGHT, VERTICAL, PanedWindow, Text
from tkinter.ttk import Notebook, Frame

from aac.ui.view_diagram_button import add_view_diagram_button

VIEWS_FRAME = None
IS_DIAGRAM_VIEW = True


def add_model_views(root_window: Tk):
    """
    Creates a view ....

    Args:
        root_window: The window to attach the models tree frame to
        view_width (int): The width of the canvas
    """
    models_view_paned_window = PanedWindow(root_window, orient=VERTICAL, showhandle=True, bg="green")

    global VIEWS_FRAME
    global IS_DIAGRAM_VIEW
    VIEWS_FRAME = models_view_paned_window

    view_width = root_window.winfo_width()
    view_height = root_window.winfo_height()

    set_diagram_view_frame(models_view_paned_window, IS_DIAGRAM_VIEW, view_width, view_height)

    models_view_paned_window.pack(side=RIGHT)
    root_window.add(models_view_paned_window)


def set_diagram_view_frame(root_frame: Frame, is_diagram_view: bool, view_width: int, view_height: int):
    print(view_width, view_height)

    button_height = 30

    if (is_diagram_view):
        view_diagram_notebook(root_frame, view_width, view_height - button_height)
    else:
        view_model_text(root_frame, view_width, view_height - button_height)

    add_view_diagram_button(root_frame, _switch_views, view_width, button_height)


def view_diagram_notebook(parent_window: PanedWindow, view_width: int, view_height: int):
    tabs_notebook = Notebook(parent_window, height=view_width, width=view_height)

    diagram_tab = _get_diagram_tab_frame(tabs_notebook, view_width, view_height)
    properties_tab = _get_properties_tab_frame(tabs_notebook, view_width, view_height)
    imports_tab = _get_imports_tab_frame(tabs_notebook, view_width, view_height)

    tabs_notebook.add(diagram_tab, text="Diagram")
    tabs_notebook.add(properties_tab, text="Properties")
    tabs_notebook.add(imports_tab, text="Imports")

    tabs_notebook.pack(fill='both', expand=True)
    parent_window.add(tabs_notebook)


def view_model_text(parent_window: PanedWindow, view_width: int, view_height: int):
    model_text_view = Text(parent_window, bg="yellow", height=view_width, width=view_height)
    model_text_view.pack(fill='both', expand=True)
    model_text_view.insert('1.0', _get_sample_model_text())
    parent_window.add(model_text_view)


def _get_diagram_tab_frame(root_notebook: Notebook, width: int, height: int) -> Frame:
    diagram_frame = Frame(root_notebook, width=width, height=height)
    Label(diagram_frame, text="test").pack()
    diagram_frame.pack(fill='both', expand=True)
    return diagram_frame


def _get_properties_tab_frame(root_notebook: Notebook, width: int, height: int) -> Frame:
    properties_frame = Frame(root_notebook)
    properties_frame.pack()
    return properties_frame


def _get_imports_tab_frame(root_notebook: Notebook, width: int, height: int) -> Frame:
    imports_frame = Frame(root_notebook)
    imports_frame.pack()
    return imports_frame


def _switch_views():
    global VIEWS_FRAME
    global IS_DIAGRAM_VIEW

    # Clear existing frames
    for widgets in VIEWS_FRAME.winfo_children():
        widgets.destroy()

    IS_DIAGRAM_VIEW = (not IS_DIAGRAM_VIEW)

    set_diagram_view_frame(VIEWS_FRAME, IS_DIAGRAM_VIEW, VIEWS_FRAME.winfo_width(), VIEWS_FRAME.winfo_height())


def _get_sample_model_text() -> str:
    """Temporary function, remove it once models are actually loaded."""
    return """---
model:
  name: Test Model A
  behavior:
    - name: Do first thing
      type: pub-sub
      acceptance:
        - scenario: A simple flow through the system
          given:
            - The system is in a valid state
          when:
            - The user does something
          then:
            - The system responds
    """
