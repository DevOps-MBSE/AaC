"""Provides the collapseable treeview of the currently loaded models."""
from tkinter import Tk, LEFT, END
from tkinter.ttk import Treeview


def get_models_treeview(parent_window: Tk) -> Treeview:
    """Creates a view containing all contextual models and definitions."""
    models_tree_view = Treeview(parent_window)

    models_id = models_tree_view.insert("", END, text="Models", open=False)
    models_tree_view.insert("", END, text="Usecase", open=False)
    models_tree_view.insert("", END, text="Data", open=False)
    models_tree_view.insert("", END, text="Enum", open=False)

    models_tree_view.insert(models_id, END, text="Test Model A", open=False)
    models_tree_view.insert(models_id, END, text="Test Model B", open=False)

    models_tree_view.pack(side=LEFT)
    return models_tree_view
