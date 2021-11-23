from tkinter import PanedWindow, Text, GROOVE


def get_model_text_view(parent_window: PanedWindow):
    model_text_view = Text(parent_window, bd=2, relief=GROOVE)
    model_text_view.insert("1.0", _get_sample_model_text())
    return model_text_view


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
