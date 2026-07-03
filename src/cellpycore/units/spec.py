"""Unit-spec dataclass for cellpy (promoted from ``cellpycore.legacy``; issue #40)."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from cellpycore.settings_base import BaseSettings

logger = logging.getLogger(__name__)


@dataclass
class CellpyUnits(BaseSettings):
    """These are the units used inside Cellpy.

    At least two sets of units needs to be defined; `cellpy_units` and `raw_units`.
    The `data.raw` dataframe is given in `raw_units` where the units are defined
    inside the instrument loader used. Since the `data.steps` dataframe is a summary of
    the step statistics from the `data.raw` dataframe, this also uses the `raw_units`.
    The `data.summary` dataframe contains columns with values directly from the `data.raw` dataframe
    given in `raw_units` as well as calculated columns given in `cellpy_units`.

    Remark that all input to cellpy through user interaction (or utils) should be in `cellpy_units`.
    This is also true for meta-data collected from the raw files. The instrument loader needs to
    take care of the translation from its raw units to `cellpy_units` during loading the raw data
    file for the meta-data (remark that this is not necessary and not recommended for the actual
    "raw" data that is going to be stored in the `data.raw` dataframe).

    As of 2022.09.29, cellpy does not automatically ensure unit conversion for input of meta-data,
    but has an internal method (`CellPyData.to_cellpy_units`) that can be used.

    These are the different attributes currently supported for data in the dataframes::

        current: str = "A"
        charge: str = "mAh"
        voltage: str = "V"
        time: str = "sec"
        resistance: str = "Ohms"
        power: str = "W"
        energy: str = "Wh"
        frequency: str = "hz"

    And here are the different attributes currently supported for meta-data::

        # output-units for specific capacity etc.
        specific_gravimetric: str = "g"
        specific_areal: str = "cm**2"  # used for calculating specific capacity etc.
        specific_volumetric: str = "cm**3"  # used for calculating specific capacity etc.

        # other meta-data
        nominal_capacity: str = "mAh/g"  # used for calculating rates etc.
        mass: str = "mg"
        length: str = "cm"
        area: str = "cm**2"
        volume: str = "cm**3"
        temperature: str = "C"

    """

    current: str = "A"
    charge: str = "mAh"
    voltage: str = "V"
    time: str = "sec"
    resistance: str = "ohm"
    power: str = "W"
    energy: str = "Wh"
    frequency: str = "hz"
    mass: str = "mg"  # for mass
    nominal_capacity: str = "mAh/g"
    specific_gravimetric: str = "g"  # g in specific capacity etc
    specific_areal: str = "cm**2"  # m2 in specific capacity etc
    specific_volumetric: str = "cm**3"  # m3 in specific capacity etc

    length: str = "cm"
    area: str = "cm**2"
    volume: str = "cm**3"
    temperature: str = "C"
    pressure: str = "bar"

    def update(self, new_units: dict):
        """Update the units."""

        logger.debug(f"{new_units=}")
        for k in new_units:
            if k in self.keys():
                self[k] = new_units[k]
