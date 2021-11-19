from tkinter import Canvas, Label, Tk, LEFT, TOP, GROOVE, Frame


def add_models_tree(root_window: Tk, view_width: int, view_height: int) -> None:
    """
    Creates a view containing all contextual models and definitions.

    Args:
        root_window: The window to attach the models tree canvas to
        view_width (int): The width of the canvas
    """
    models_tree_frame = Frame(root_window, width=view_width, height=view_height, bg="green")
    models_tree_frame.pack(fill="both", side=LEFT)

    # models_label = Label(models_tree_frame, text="Test")
    # models_label.pack()

    # models_tree_entry = Entry(root_window)
    # models_tree_canvas.create_window(view_width // 2, 20, window=models_tree_entry)

