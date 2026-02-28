from PyQt6.QtWidgets import QPushButton

class PrintButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.clicked.connect(self.print_message)

    def print_message(self):
        print(f"{self.text()} was clicked :D !")