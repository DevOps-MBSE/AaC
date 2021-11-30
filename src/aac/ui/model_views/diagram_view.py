"""Provides the model diagram views."""
from tkinter import (
    PanedWindow,
    Canvas,
    Frame,
    TOP,
    BOTTOM,
    RIDGE,
)
from tkinter.ttk import Notebook

from aac.ui.components.LabeledInputList import LabeledInputList
from aac.ui.components.LabeledInput import LabeledInput
from aac.ui.components.ColoredCircle import ColoredCircle


def get_diagram_view(parent_window: PanedWindow):
    tabs_notebook = Notebook(parent_window)

    diagram_tab = _get_diagram_tab_frame(tabs_notebook)
    properties_tab = _get_properties_tab_frame(tabs_notebook)
    imports_tab = _get_imports_tab_frame(tabs_notebook)

    tabs_notebook.add(diagram_tab, text="Diagram")
    tabs_notebook.add(properties_tab, text="Properties")
    tabs_notebook.add(imports_tab, text="Imports")
    return tabs_notebook


def _get_diagram_tab_frame(root_notebook: Notebook) -> Frame:
    diagram_frame = Frame(root_notebook, borderwidth=3, relief=RIDGE)
    diagram_frame.pack(fill="both", expand=True)

    # Using a second layer frame for content in the notebook page since the frame diagram_frame doesn't seem to respect styling via pack()
    diagram_content_frame = Frame(diagram_frame)
    diagram_content_frame.pack(anchor="n", fill="both", expand=True, padx=25)

    model_canvas = Canvas(diagram_content_frame)
    model_canvas.pack(side=TOP, fill="both", expand=True)

    # Replace these with the model diagram content
    model_canvas.create_line(0, 0, 2000, 1129)
    model_canvas.create_line(0, 960, 1700, 0)

    # Validation Indicator #
    validation_indicator = ColoredCircle(diagram_content_frame, "green").build()
    validation_indicator.pack(anchor="e")

    return diagram_frame


def _get_properties_tab_frame(root_notebook: Notebook) -> Frame:
    properties_frame = Frame(root_notebook, borderwidth=3, relief=RIDGE)
    properties_frame.pack(fill="both", expand=True)

    # Using a second layer frame for content in the notebook page since the frame properties_frame doesn't seem to respect styling via pack()
    properties_content_frame = Frame(properties_frame)
    properties_content_frame.pack(anchor="n", fill="x", expand=True, padx=25)

    # Properties Name Frame #
    properties_name_frame = LabeledInput(
        label_text="Name", input_value="Test Model A", parent_widget=properties_content_frame
    ).build()

    # Properties Description Frame #
    properties_description_frame = LabeledInput(
        label_text="Description", input_value="", parent_widget=properties_content_frame
    ).build()

    # Properties Components Frame #
    properties_components_frame = Frame(properties_content_frame)
    properties_components_frame.pack(fill="x", expand=True)

    properties_components_listbox_frame = LabeledInputList(
        parent_widget=properties_components_frame,
        listbox_label_text="Model Components",
        listbox_content=["Component 1", "Component 2"],
        input_label_text="Components",
        input_content="Component 3",
    ).build()

    # Properties Behavior Frame #
    properties_behavior_frame = Frame(properties_content_frame)
    properties_behavior_frame.pack(fill="x", expand=True)

    properties_behavior_listbox_frame = LabeledInputList(
        parent_widget=properties_behavior_frame,
        listbox_label_text="Model Behaviors",
        listbox_content=["Behavior 1"],
        input_label_text="Behavior",
        input_content="Behavior 2",
    ).build()

    # Validation Indicator #
    validation_indicator = ColoredCircle(properties_content_frame, "green").build()
    validation_indicator.pack(anchor="e")

    return properties_frame


def _get_imports_tab_frame(root_notebook: Notebook) -> Frame:
    imports_tab_frame = Frame(root_notebook, borderwidth=3, relief=RIDGE)
    imports_tab_frame.pack(fill="both", expand=True)

    # Using a second layer frame for content in the notebook page since the frame properties_frame doesn't seem to respect styling via pack()
    imports_tab_content_frame = Frame(imports_tab_frame)
    imports_tab_content_frame.pack(anchor="n", fill="x", expand=True, padx=25)

    # Imports Frame #
    imports_list_frame = Frame(imports_tab_content_frame)
    imports_list_frame.pack(fill="x", expand=True)

    imports_listbox_frame = LabeledInputList(
        parent_widget=imports_list_frame,
        listbox_label_text="Imports",
        listbox_content=["Imported Enum Data", "Imported Data"],
        input_label_text="Name",
        input_content="",
    ).build()

    # Validation Indicator #
    validation_indicator = ColoredCircle(imports_tab_content_frame, "green").build()
    validation_indicator.pack(side=BOTTOM, anchor="se")

    return imports_tab_frame


def not_implemented():
    print("Not implemented")
