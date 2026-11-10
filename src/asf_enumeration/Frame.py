from dataclasses import dataclass
from typing import TypedDict
from asf_enumeration.aria_s1_gunw import FlightDirections
import shapely


class AriaMetadata:
    """ARIA specific frame metadata"""


class BurstMetadata:
    """SLC Burst specific frame metadata"""


class NisarMetadata:
    """NISAR specific frame metadata"""


class AriaOptions(TypedDict):
    """ARIA specific options for querying frames"""

    flightDirection: FlightDirections
    path: int
    pass


class BurstOptions(TypedDict):
    """SLC Burst specific options for querying frames"""

    flightDirection: FlightDirections
    subswath: str
    pass


class NisarOptions(TypedDict):
    """NISAR specific options for querying frames"""

    pass


Metadata = AriaMetadata | BurstMetadata | NisarMetadata
Options = AriaOptions | BurstOptions | NisarOptions


@dataclass
class Frame:
    id: str
    polygon: shapely.Polygon
    flightDirection: FlightDirections
    type: str
    metadata: Metadata
