from dataclasses import dataclass
from typing import TypedDict

import shapely

from asf_enumeration.aria_s1_gunw import FlightDirections


class AriaMetadata:
    """ARIA specific frame metadata."""


class BurstMetadata:
    """SLC Burst specific frame metadata."""


class NisarMetadata:
    """NISAR specific frame metadata."""


class AriaOptions(TypedDict):
    """ARIA specific options for querying frames."""

    flightDirection: FlightDirections
    path: int


class BurstOptions(TypedDict):
    """SLC Burst specific options for querying frames."""

    flightDirection: FlightDirections
    subswath: str


class NisarOptions(TypedDict):
    """NISAR specific options for querying frames."""


Metadata = AriaMetadata | BurstMetadata | NisarMetadata
Options = AriaOptions | BurstOptions | NisarOptions


@dataclass
class Frame:
    """Basic class for representing a spatial frame across datasets."""

    id: str
    polygon: shapely.Polygon
    flightDirection: FlightDirections
    type: str
    metadata: Metadata
