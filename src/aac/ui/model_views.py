from tkinter import Tk, TOP, Label, VERTICAL, PanedWindow, Text, Widget, BOTTOM, GROOVE, Canvas, CENTER
from tkinter.ttk import Notebook, Frame

from attr import attrs, attrib, validators

from aac.ui.view_diagram_button import get_view_diagram_button

WIDGETS_MANAGER = None


def add_model_views(root_window: Tk):
    """
    Creates a view ....

    Args:
        root_window: The window to attach the models tree frame to
    """
    models_view_paned_window = PanedWindow(root_window, orient=VERTICAL, showhandle=True)

    global WIDGETS_MANAGER
    WIDGETS_MANAGER = ViewWidgetsManager(models_view_paned_window)
    WIDGETS_MANAGER.set_view_toggle_button(
        get_view_diagram_button(models_view_paned_window, WIDGETS_MANAGER.toggle_view)
    )

    diagrams_views = _get_diagram_notebook_view(WIDGETS_MANAGER.parent_window)
    textual_view = _get_model_text_view(WIDGETS_MANAGER.parent_window)

    WIDGETS_MANAGER.add_view(diagrams_views)
    WIDGETS_MANAGER.add_view(textual_view)

    root_window.add(models_view_paned_window)


def _get_diagram_notebook_view(parent_window: PanedWindow):
    tabs_notebook = Notebook(parent_window)

    diagram_tab = _get_diagram_tab_frame(tabs_notebook)
    properties_tab = _get_properties_tab_frame(tabs_notebook)
    imports_tab = _get_imports_tab_frame(tabs_notebook)

    tabs_notebook.add(diagram_tab, text="Diagram")
    tabs_notebook.add(properties_tab, text="Properties")
    tabs_notebook.add(imports_tab, text="Imports")
    return tabs_notebook


def _get_model_text_view(parent_window: PanedWindow):
    model_text_view = Text(parent_window, bd=2, relief=GROOVE)
    model_text_view.insert("1.0", _get_sample_model_text())
    return model_text_view


def _get_diagram_tab_frame(root_notebook: Notebook) -> Frame:
    diagram_frame = Frame(root_notebook)
    diagram_frame.pack(fill="both", expand=True)

    model_canvas = Canvas(diagram_frame)
    model_canvas.pack(side=TOP, fill="both", expand=True)

    # Replace these with the model diagram content
    model_canvas.create_line(0, 0, 2000, 1129)
    model_canvas.create_line(0, 960, 1700, 0)

    return diagram_frame


def _get_properties_tab_frame(root_notebook: Notebook) -> Frame:
    properties_frame = Frame(root_notebook)
    properties_frame.pack(fill="both", expand=True)
    return properties_frame


def _get_imports_tab_frame(root_notebook: Notebook) -> Frame:
    imports_frame = Frame(root_notebook)
    imports_frame.pack()
    return imports_frame


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


@attrs
class ViewWidgetsManager:
    """This class provides persistent management of the various model views and transitions between them."""

    parent_window = attrib(validator=validators.instance_of(Widget))
    current_view = attrib(default=None, validator=validators.instance_of((Widget, type(None))))
    available_views = attrib(default=[], validator=validators.instance_of(list))
    view_toggle_button = attrib(
        default=None, validator=validators.instance_of((Widget, type(None)))
    )

    def set_view_toggle_button(self, button: Frame):
        """Sets the widget that represents the botton used to toggle between model text views and model diagram views."""
        self.view_toggle_button = button
        self.parent_window.add(self.view_toggle_button)

    def add_view(self, widget: Widget):
        """Register a view to toggle between."""
        self.available_views.append(widget)

        # If a current view isn't set yet, set it to our new view.
        if not self.current_view:
            self.current_view = widget
            self._pack_models_view_widget(self.current_view)

    def toggle_view(self):
        """Transition between registered views."""

        if self._are_available_views_populated():

            previous_view = self.current_view

            # If no view is set, set the initial one
            if self.current_view not in self.available_views:
                self.current_view = self.available_views[0]
            else:
                current_view_index = self.available_views.index(self.current_view)

                # Increment or roll over to 0
                current_view_index = (current_view_index + 1) % len(self.available_views)
                self.current_view = self.available_views[current_view_index]

            if previous_view:
                previous_view.pack_forget()

            self._pack_models_view_widget(self.current_view)

        else:
            print("Err available views not populated.")

    def _are_available_views_populated(self):
        return len(self.available_views) > 0

    def _pack_models_view_widget(self, widget: Widget):
        widget.pack(fill="both", expand=True, side=TOP)
        self._repack_button()

    def _repack_button(self):
        self.view_toggle_button.pack_forget()
        self.view_toggle_button.pack(side=BOTTOM, anchor="se", expand=False, fill="none")
