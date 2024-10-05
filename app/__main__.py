import sys

from dependency_injector.wiring import Provide, inject
from PySide6 import QtWidgets

from .container import Container
from .window import Window


@inject
def main(window: Window = Provide[Container.window]):
    window.show()


app = QtWidgets.QApplication([])

container = Container()
container.core.init_resources()
container.wire(modules=[__name__])

main()

sys.exit(app.exec())
