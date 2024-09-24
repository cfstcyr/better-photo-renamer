from dataclasses import dataclass, field


@dataclass
class GroupingArgs:
    method: str
    group_cols: list[str]
    params: dict = field(default_factory=dict)
