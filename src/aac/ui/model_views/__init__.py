"""Provides the overall model views widget featuring toggleable views."""
from tkinter import Tk, TOP, VERTICAL, PanedWindow, Widget, BOTTOM, Frame

from attr import attrs, attrib, validators

from aac.ui.model_views import diagram_view, text_view, toggle_view_diagram_button

WIDGETS_MANAGER = None


def get_model_views(root_window: Tk) -> PanedWindow:
    """
    Creates the main model views (text and diagram).

    Args:
        root_window: The window to attach the models tree frame to

    Returns:
        tkinter.PanedWindow with the various model views.
    """
    models_view_paned_window = PanedWindow(root_window, orient=VERTICAL, showhandle=True)

    global WIDGETS_MANAGER
    WIDGETS_MANAGER = ViewWidgetsManager(models_view_paned_window)
    WIDGETS_MANAGER.set_view_toggle_button(
        toggle_view_diagram_button.get_view_diagram_button(
            models_view_paned_window, WIDGETS_MANAGER.toggle_view
        )
    )

    diagrams_views = diagram_view.get_diagram_view(WIDGETS_MANAGER.parent_window)
    textual_view = text_view.get_model_text_view(WIDGETS_MANAGER.parent_window)

    WIDGETS_MANAGER.add_view(diagrams_views)
    WIDGETS_MANAGER.add_view(textual_view)

    return models_view_paned_window


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
            print("Error: available views not populated.")

    def _are_available_views_populated(self):
        return len(self.available_views) > 0

    def _pack_models_view_widget(self, widget: Widget):
        widget.pack(fill="both", expand=True, side=TOP)
        self._repack_button()

    def _repack_button(self):
        self.view_toggle_button.pack_forget()
        self.view_toggle_button.pack(side=BOTTOM, anchor="se", expand=False, fill="none")
