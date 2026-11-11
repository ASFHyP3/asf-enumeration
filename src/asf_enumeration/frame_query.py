"""Generic get_frames method for spatial frame querying."""

import shapely
from asf_search import validate_wkt

from asf_enumeration.s1_burst import get_slc_burst_ids

from .Frame import AriaMetadata, Frame, Options
from .aria_s1_gunw import get_frames as get_aria_frames


def get_frames(
    type: str,
    intersectsWith: str | shapely.geometry.base.BaseGeometry,
    maxResults: int = 250,
    options: Options | None = None,
) -> list[Frame] | None:
    """Get frames for a given dataset over a given aoi.

    Args:
        type: Type of frames to query. Either 'BURST', 'ARIA', or 'NISAR'
        intersectsWith: the AOI to query with
        maxResults: How many frames to limit results to
        options: Relevant options for different frame types
    """
    if type == 'BURST':
        return get_slc_burst_ids(intersectsWith=intersectsWith, maxResults=maxResults, *options)
    elif type == 'ARIA':
        return _get_aria_frame_ids(intersectsWith, options)
    elif type == 'NISAR':
        return []


def _get_aria_frame_ids(
    intersectsWith: shapely.geometry.base.BaseGeometry | str, options: Options
) -> list[Frame]:
    if isinstance(intersectsWith, str):
        intersectsWith, _, __ = validate_wkt(intersectsWith)
    return [
        Frame(str(frame.id), frame.polygon, frame.flight_direction, 'ARIA', AriaMetadata())
        for frame in get_aria_frames(intersectsWith, *options)
    ]
