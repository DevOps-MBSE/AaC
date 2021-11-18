from tkinter import Tk

from aac.ui.menu_bar import menu_bar


def main_window() -> None:
    """Runs the main AaC UI window."""
    main_window = Tk()
    main_window.title("Architecture-as-Code")

    width, height = _get_window_dimensions(main_window)
    main_window.geometry("%dx%d" % (width, height))
    main_window_menu_bar = menu_bar(main_window)
    main_window.config(menu=main_window_menu_bar)

    return main_window


def _get_window_dimensions(window) -> tuple[int, int]:
    """
    Gets the window width and height and returns them in a tuple.

    Returns
        Tuple of window width and window height
    """
    return (window.winfo_screenwidth(), window.winfo_screenheight())
