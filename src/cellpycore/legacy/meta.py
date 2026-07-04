"""Legacy cellpy metadata placeholders."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Meta:
    pass


class MockMetaTestDependent(Meta):
    """Graceful-degradation metadata placeholder on ``Data``.

    ``cycle_mode`` is optional. ``None`` (the default) means normal full-cell /
    cathode convention at the engine boundary; set ``"anode"`` explicitly for
    half-cell (inverted) tests. Legacy cellpy historically defaulted to
    ``"anode"`` — the cellpy bridge must set that when loading real cells, not
    rely on this placeholder default.
    """

    cycle_mode: Optional[str] = None
