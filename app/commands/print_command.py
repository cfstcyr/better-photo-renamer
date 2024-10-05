from dataclasses import dataclass

from app.commands import Command


@dataclass
class PrintCommand(Command):
    text: str

    def do(self):
        print(self.text)

    def undo(self):
        print(f"Undoing print of {self.text}")
