from PySide6 import QtWidgets

from app.commands import PrintCommand
from app.services import CommandService


class BottomBarSection(QtWidgets.QWidget):
    command_service: CommandService

    def __init__(self, command_service: CommandService):
        super().__init__()

        self.command_service = command_service

        self.setLayout(self._create_layout())

    def _create_layout(self) -> QtWidgets.QLayout:
        layout = QtWidgets.QVBoxLayout()

        label = QtWidgets.QLabel("Bottom bar Section")
        layout.addWidget(label)

        button = QtWidgets.QPushButton("Print")
        button.clicked.connect(
            lambda: self.command_service.execute(PrintCommand("Bottom bar Section"))
        )
        layout.addWidget(button)

        return layout
