from PySide6 import QtWidgets


class ConfigSection(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.vbox_layout = QtWidgets.QVBoxLayout()

        self.label = QtWidgets.QLabel("Config Section")
        self.vbox_layout.addWidget(self.label)

        self.setLayout(self.vbox_layout)
