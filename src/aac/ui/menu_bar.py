"""Provides the main application window's menu bar."""
from tkinter import Menu, Tk


def donothing():
    print("Do nothing!")


def menu_bar(root_window: Tk) -> Menu:
    """
    Creates and returns the AaC UI menu bar.

    Args:
        root_window (Tk): the window to attach the menu to

    Returns:
        The menu bar.
    """
    menu_bar = Menu(root_window, tearoff=0)
    _add_file_menu(menu_bar)
    _add_edit_menu(menu_bar)
    _add_view_menu(menu_bar)
    _add_help_menu(menu_bar)

    return menu_bar


def _add_file_menu(root_menu: Menu) -> None:
    """Configures the file menu dropdown."""
    file_menu = Menu(root_menu, tearoff=0)

    file_menu.add_command(label="New File", command=donothing)
    file_menu.add_command(label="Open File", command=donothing)
    file_menu.add_command(label="Save File", command=donothing)

    root_menu.add_cascade(label="File", menu=file_menu)


def _add_edit_menu(root_menu: Menu) -> None:
    """Configures the edit menu dropdown."""
    edit_menu = Menu(root_menu, tearoff=0)

    edit_menu.add_command(label="Undo", command=donothing)
    edit_menu.add_command(label="Redo", command=donothing)
    edit_menu.add_command(label="Cut", command=donothing)
    edit_menu.add_command(label="Copy", command=donothing)
    edit_menu.add_command(label="Paste", command=donothing)
    edit_menu.add_command(label="Find", command=donothing)

    root_menu.add_cascade(label="Edit", menu=edit_menu)


def _add_view_menu(root_menu: Menu) -> None:
    """Configures the view menu dropdown."""
    view_menu = Menu(root_menu, tearoff=0)

    root_menu.add_cascade(label="View", menu=view_menu)


def _add_help_menu(root_menu: Menu) -> None:
    """Configures the help menu dropdown."""
    help_menu = Menu(root_menu, tearoff=0)
    help_menu.add_command(label="About", command=donothing)

    root_menu.add_cascade(label="Help", menu=help_menu)
