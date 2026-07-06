"""Experimental BDF (Battery Data Format) read/export prototype.

Not part of the cellpy-core public API. See the placement decision in
``.issueflows/04-designs-and-guides/bdf-io-placement.md`` (issue #100) and the
BDF spec at
https://battery-data-alliance.github.io/battery-data-format-ontology/battery-data-format.html
"""

from cellpy_bdf.export import export_bdf
from cellpy_bdf.mapping import bdf_mapping
from cellpy_bdf.read import read_bdf

__all__ = ["bdf_mapping", "export_bdf", "read_bdf"]
__version__ = "0.1.0"
