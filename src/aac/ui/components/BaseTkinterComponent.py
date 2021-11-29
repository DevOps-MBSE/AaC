from attr import attrs, attrib


@attrs
class BaseTkinterComponent:
    """Base class for all custom Tkinter components."""

    parent_widget = attrib()

    def build(self):
        raise NotImplementedError()
