import logging

from reactivex import observable, subject
from reactivex import operators as op

from app.commands import Command


class CommandService:
    _history: subject.BehaviorSubject[list[Command]]
    can_undo: observable.Observable[bool]
    __logger: logging.Logger

    def __init__(self):
        self.__logger = logging.getLogger(self.__class__.__name__)
        self._history = subject.BehaviorSubject([])
        self.can_undo = self._history.pipe(op.map(lambda history: bool(history)))

    def execute(self, command: Command):
        self.__logger.info(f"Executing command {command}")
        command.do()
        self._history.on_next(self._history.value + [command])

    def undo(self):
        if self._history.value:
            command = self._history.value.pop()
            self.__logger.info(f"Undoing command {command}")
            command.undo()
            self._history.on_next(self._history.value)
