from typing import Optional

from rich.console import Console


def confirm(msg: str, default: Optional[bool] = None) -> bool:
    console = Console()

    while True:
        response = console.input(f"{msg} (y/n): ").lower()
        if response in ["y", "yes"]:
            return True
        elif response in ["n", "no"]:
            return False
        elif not response and default is not None:
            return default
        else:
            console.print("Please answer with 'y' or 'n'")
