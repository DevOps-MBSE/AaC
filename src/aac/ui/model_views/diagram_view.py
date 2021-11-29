from tkinter import (
    font,
    PanedWindow,
    Canvas,
    Text,
    Button,
    Listbox,
    Frame,
    Label,
    LEFT,
    RIGHT,
    CENTER,
    END,
    TOP,
    BOTTOM,
    RIDGE,
)
from tkinter.ttk import Notebook
from tkinter.font import BOLD
from attr import attrs, attrib


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

    return diagram_frame


def _get_properties_tab_frame(root_notebook: Notebook) -> Frame:
    properties_frame = Frame(root_notebook, borderwidth=3, relief=RIDGE)
    properties_frame.pack(fill="both", expand=True)

    # Using a second layer frame for content in the notebook page since the frame properties_frame doesn't seem to respect styling via pack()
    properties_content_frame = Frame(properties_frame)
    properties_content_frame.pack(anchor="n", fill="x", expand=True, padx=25)

    # Properties Name Frame #
    properties_name_frame = LabeledInput(
        label_text="Name", input_value="A", parent_widget=properties_content_frame
    ).build()

    # Properties Description Frame #
    properties_description_frame = LabeledInput(
        label_text="Description", input_value="", parent_widget=properties_content_frame
    ).build()

    # Properties Components Frame #
    properties_components_frame = Frame(properties_content_frame)
    properties_components_frame.pack(fill="x", expand=True)

    properties_components_insert_new_frame = InsertNewItemInput(
        label_text="Components",
        input_value="Component 3",
        parent_widget=properties_components_frame,
        button_command_callable=not_implemented,
    ).build()

    properties_components_listbox_frame = LabeledListBox(
        label_text="Model Components",
        parent_widget=properties_components_frame,
        listbox_content=["Component 1", "Component 2"],
    ).build()

    # Properties Behavior Frame #
    properties_behavior_frame = Frame(properties_content_frame)
    properties_behavior_frame.pack(fill="x", expand=True)

    properties_behavior_insert_new_frame = InsertNewItemInput(
        label_text="Behavior",
        input_value="Behavior 2",
        parent_widget=properties_behavior_frame,
        button_command_callable=not_implemented,
    ).build()

    properties_behavior_listbox_frame = LabeledListBox(
        label_text="Model Behaviors",
        parent_widget=properties_behavior_frame,
        listbox_content=["Behavior 1"],
    ).build()

    return properties_frame


def _get_imports_tab_frame(root_notebook: Notebook) -> Frame:
    imports_tab_frame = Frame(root_notebook, borderwidth=3, relief=RIDGE)
    imports_tab_frame.pack(fill="both", expand=True)

    # Using a second layer frame for content in the notebook page since the frame properties_frame doesn't seem to respect styling via pack()
    imports_tab_content_frame = Frame(imports_tab_frame)
    imports_tab_content_frame.pack(anchor="n", fill="x", expand=True, padx=25)

    # Model Imports #
    imports_insert_new_frame = InsertNewItemInput(
        label_text="Name",
        input_value="",
        parent_widget=imports_tab_content_frame,
        button_command_callable=not_implemented,
    ).build()

    imports_listbox_frame = LabeledListBox(
        label_text="Imports",
        parent_widget=imports_tab_content_frame,
        listbox_content=["Imported Enum Data", "Imported Data"],
    ).build()

    return imports_tab_frame


def not_implemented():
    print("Not implemented")


@attrs
class BaseTkinterComponent:
    """Base class for all custom Tkinter components."""

    parent_widget = attrib()

    def build(self):
        raise NotImplementedError()


@attrs
class LabeledInput(BaseTkinterComponent):
    """
    Component class for labeled text input.

    Returns:
        A frame with a label and text input.
    """

    label_text = attrib()
    input_value = attrib()

    def build(self):
        frame = Frame(self.parent_widget)
        frame.pack(side=TOP, fill="x", expand=True, pady=10)

        properties_components_label = Label(frame, text=self.label_text)
        properties_components_label.pack(side=LEFT, padx=(0, 20))

        text = Text(frame, height=1)
        text.insert(END, self.input_value)
        text.pack(side=LEFT, fill="x", expand=True)
        return frame


@attrs
class InsertNewItemInput(LabeledInput):
    """
    Component class for a labeled input used to insert new items.

    Returns:
        A frame with a label and text input.
    """

    button_command_callable = attrib()

    def build(self):
        frame = LabeledInput.build(self)

        plus_button_font = font.Font(size=11, weight=BOLD)
        plus_button = Button(
            frame, text="+", command=self.button_command_callable, font=plus_button_font
        )
        plus_button.pack(side=RIGHT, padx=(20, 0))

        return frame


@attrs
class LabeledListBox(BaseTkinterComponent):
    """
    Component class for a labeled list box.

    Returns:
        A frame with a label and listbox.
    """

    listbox_content = attrib()
    label_text = attrib()

    def build(self):
        frame = Frame(self.parent_widget)
        frame.pack(side=BOTTOM, fill="x", expand=True, pady=10)

        listbox_frame = Frame(self.parent_widget, borderwidth=3, relief=RIDGE)
        listbox_frame.pack(side=BOTTOM, fill="x", expand=True)

        listbox_frame_label = Label(listbox_frame, text=self.label_text)
        listbox_frame_label.pack(side=TOP)

        listbox = Listbox(listbox_frame)

        for entry in self.listbox_content:
            listbox.insert(END, entry)

        listbox.pack(side=BOTTOM, fill="x", expand=True)

        return frame
