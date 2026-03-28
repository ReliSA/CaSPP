"""
A simple button widget that prints a message when clicked.
"""

# NOTE: Placeholder for future custom buttons

# third-party imports
from PyQt6.QtWidgets import QPushButton

class PrintButton(QPushButton):
    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.clicked.connect(self.print_message)

    def print_message(self) -> None:
        print(f"{self.text()} was clicked :D !")