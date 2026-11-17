"""Generic get_frames method for spatial frame querying."""

import shapely

from asf_enumeration.aria_s1_gunw import get_aria_frame_ids
from asf_enumeration.s1_burst import get_slc_burst_frame_ids

from .frame import Frame, Options


def get_frame_ids(
    type: str,
    intersectsWith: str | shapely.geometry.base.BaseGeometry,
    maxResults: int = 250,
    options: Options | None = None,
) -> list[Frame]:
    """Get frames for a given dataset over a given aoi.

    Args:
        type: Type of frames to query. Either 'SLC-BURST', 'ARIA S1 GUNW'
        intersectsWith: the AOI to query with
        maxResults: How many frames to limit results to
        options: Relevant options for different frame types
    """
    if intersectsWith is None:
        raise FrameQueryError('expected AOI (`intersectsWith`) to query with')

    if options is None:
        options = {}

    if type == 'SLC-BURST':
        return get_slc_burst_frame_ids(intersectsWith, maxResults=maxResults, options=options)
    elif type == 'ARIA S1 GUNW':
        return get_aria_frame_ids(intersectsWith, maxResults=maxResults, options=options)

    raise FrameQueryError(
        f'Unsupported argument passed to `type`. Expected `SLC-BURST` or `ARIA S1 GUNW`. Got `{type}`'
    )


class FrameQueryError(Exception):
    """Exception for errors with Frame Queries."""
