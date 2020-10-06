from dataclasses import field
from typing import Dict, FrozenSet


def default_field(obj):
    return field(default_factory=lambda: obj)


def slots(anotes: Dict[str, object]) -> FrozenSet[str]:
    """ https://stackoverflow.com/a/63658478/3827785 """
    return frozenset(anotes.keys())
