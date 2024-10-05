from PySide6 import QtWidgets

from app.services import CommandService

from . import sections


class Window(QtWidgets.QMainWindow):
    layout: QtWidgets.QLayout

    command_service: CommandService

    config_section: sections.ConfigSection
    files_section: sections.FilesSection
    bottom_bar_section: sections.BottomBarSection
    toolbar_section: sections.ToolbarSection

    def __init__(
        self,
        *,
        command_service: CommandService,
        config_section: sections.ConfigSection,
        files_section: sections.FilesSection,
        bottom_bar_section: sections.BottomBarSection,
        toolbar_section: sections.ToolbarSection,
    ) -> None:
        super().__init__()

        self.command_service = command_service

        self.config_section = config_section
        self.files_section = files_section
        self.bottom_bar_section = bottom_bar_section
        self.toolbar_section = toolbar_section

        self.resize(800, 600)
        self.setWindowTitle("Hello World")

        self.layout = self._create_layout()
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)

        self.addToolBar(self.toolbar_section)

    def _create_layout(self) -> QtWidgets.QLayout:
        layout = QtWidgets.QGridLayout()

        layout.addWidget(self.config_section, 0, 0)
        layout.addWidget(self.files_section, 0, 1)
        layout.addWidget(self.bottom_bar_section, 1, 0, 1, 2)

        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 0)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)

        return layout
