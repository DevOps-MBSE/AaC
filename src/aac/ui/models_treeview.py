"""Provides the collapseable treeview of the currently loaded models."""
from tkinter import Tk, LEFT, END
from tkinter.ttk import Treeview


def add_models_treeview(parent_window: Tk) -> None:
    """Creates a view containing all contextual models and definitions."""
    models_tree_view = Treeview(parent_window)

    # TODO: This will need to be generated from the loaded models
    models_id = models_tree_view.insert("", END, text="Models", open=False)
    models_tree_view.insert("", END, text="Usecase", open=False)
    models_tree_view.insert("", END, text="Data", open=False)
    models_tree_view.insert("", END, text="Enum", open=False)

    models_tree_view.insert(models_id, END, text="A", open=False)
    models_tree_view.insert(models_id, END, text="B", open=False)

    models_tree_view.pack(side=LEFT)

    parent_window.add(models_tree_view)
