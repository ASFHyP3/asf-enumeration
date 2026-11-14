"""Class definitions for generic spatial frame querying."""

from dataclasses import dataclass
from typing import TypedDict

import shapely

from asf_enumeration.aria_s1_gunw import FlightDirections


@dataclass
class AriaMetadata:
    """ARIA specific frame metadata."""


@dataclass
class BurstMetadata:
    """SLC Burst specific frame metadata."""


@dataclass
class NisarMetadata:
    """NISAR specific frame metadata."""


class AriaOptions(TypedDict):
    """ARIA specific options for querying frames."""

    flight_direction: FlightDirections | None
    path: int | None


class BurstOptions(TypedDict):
    """SLC Burst specific options for querying frames."""

    path: int | None
    flight_direction: FlightDirections | None
    subswath: str | None


class NisarOptions(TypedDict):
    """NISAR specific options for querying frames."""


Metadata = AriaMetadata | BurstMetadata | NisarMetadata
Options = AriaOptions | BurstOptions | NisarOptions


@dataclass
class Frame:
    """Basic class for representing a spatial frame across datasets."""

    id: str
    polygon: shapely.Polygon
    flight_direction: FlightDirections
    type: str
    metadata: Metadata
