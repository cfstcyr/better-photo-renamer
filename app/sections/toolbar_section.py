from PySide6 import QtGui, QtWidgets

from app.services.command_service import CommandService


class ToolbarSection(QtWidgets.QToolBar):
    command_service: CommandService

    def __init__(self, command_service: CommandService):
        super().__init__()

        self.command_service = command_service

        self._create_actions()

        self.command_service.can_undo.subscribe(
            on_next=lambda can_undo: self.undo_action.setEnabled(can_undo)
        )

    def _create_actions(self):
        self.undo_action = QtGui.QAction(
            icon=self.style().standardIcon(
                QtWidgets.QStyle.StandardPixmap.SP_ArrowLeft
            ),
            text="Undo",
            parent=self,
        )
        self.undo_action.triggered.connect(lambda: self.command_service.undo())

        self.addActions([self.undo_action])
