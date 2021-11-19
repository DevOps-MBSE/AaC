from tkinter import Tk, TOP, NW, Label, Canvas, Entry, RIGHT, VERTICAL, PanedWindow, Text, N, S, W, E
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
    models_view_paned_window = PanedWindow(root_window, orient=VERTICAL, showhandle=True, bg="red")

    global VIEWS_FRAME
    global IS_DIAGRAM_VIEW
    VIEWS_FRAME = models_view_paned_window

    _set_diagram_view_frame(models_view_paned_window, IS_DIAGRAM_VIEW)

    root_window.add(models_view_paned_window)


def _set_diagram_view_frame(parent_window: PanedWindow, is_diagram_view: bool):

    button_height = 40
    window_height = parent_window.winfo_height() if parent_window.winfo_height() > 1 else button_height * 2
    window_width = parent_window.winfo_width() if parent_window.winfo_width() > 1 else button_height * 2

    models_view = _view_diagram_notebook(parent_window) if is_diagram_view else _view_model_text(parent_window)
    parent_window.add(models_view)

    diagram_button = add_view_diagram_button(parent_window, _switch_views)
    parent_window.add(diagram_button)

    parent_window.paneconfig(models_view, width=window_width, height=window_height - button_height * 2, sticky=N + W + E + S)
    parent_window.paneconfig(diagram_button, height=button_height, sticky=S + E)


def _view_diagram_notebook(parent_window: PanedWindow):
    tabs_notebook = Notebook(parent_window)

    diagram_tab = _get_diagram_tab_frame(tabs_notebook)
    properties_tab = _get_properties_tab_frame(tabs_notebook)
    imports_tab = _get_imports_tab_frame(tabs_notebook)

    tabs_notebook.add(diagram_tab, text="Diagram")
    tabs_notebook.add(properties_tab, text="Properties")
    tabs_notebook.add(imports_tab, text="Imports")

    tabs_notebook.pack(fill="both", expand=True, side=TOP)
    return tabs_notebook


def _view_model_text(parent_window: PanedWindow):
    model_text_view = Text(parent_window, bg="yellow")
    model_text_view.pack(fill="both", expand=True)
    model_text_view.insert("1.0", _get_sample_model_text())
    return model_text_view


def _get_diagram_tab_frame(root_notebook: Notebook) -> Frame:
    diagram_frame = Frame(root_notebook)
    Label(diagram_frame, text="test").pack(fill="both", expand=True)

    model_text_view = Text(diagram_frame, bg="yellow")
    model_text_view.pack(fill="both", expand=True)
    model_text_view.insert("1.0", "")

    diagram_frame.pack(fill="both", expand=True)
    return diagram_frame


def _get_properties_tab_frame(root_notebook: Notebook) -> Frame:
    properties_frame = Frame(root_notebook)
    properties_frame.pack(fill="both", expand=True)
    return properties_frame


def _get_imports_tab_frame(root_notebook: Notebook) -> Frame:
    imports_frame = Frame(root_notebook)
    imports_frame.pack()
    return imports_frame


def _switch_views():
    global VIEWS_FRAME
    global IS_DIAGRAM_VIEW

    # Clear existing frames
    # TODO FIXME This is cuasing weird behavior like the button not changing state since it's being killed every update.
    # leverage add() and forget() instead https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/panedwindow.html
    for widgets in VIEWS_FRAME.winfo_children():
        widgets.destroy()

    IS_DIAGRAM_VIEW = not IS_DIAGRAM_VIEW

    _set_diagram_view_frame(VIEWS_FRAME, IS_DIAGRAM_VIEW)


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
