"""Generic get_frames method for spatial frame querying."""

import shapely
from asf_search import validate_wkt

from asf_enumeration.s1_burst import get_slc_burst_ids

from .aria_s1_gunw import get_frames
from .frame import AriaMetadata, Frame, Options


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
        return get_slc_burst_ids(
            intersectsWith,
            **options,  # type: ignore[unused-ignore]
            maxResults=maxResults,
        )
    elif type == 'ARIA S1 GUNW':
        return _get_aria_frame_ids(intersectsWith, maxResults=maxResults, options=options)

    raise FrameQueryError(
        f'Unsupported argument passed to `type`. Expected `SLC-BURST` or `ARIA S1 GUNW`. Got `{type}`'
    )


def _get_aria_frame_ids(
    intersectsWith: shapely.geometry.base.BaseGeometry | str, maxResults: int, options: Options
) -> list[Frame]:
    if isinstance(intersectsWith, str):
        intersectsWith, _, __ = validate_wkt(intersectsWith)
    return [
        Frame(
            id=str(frame.id),
            polygon=frame.polygon,
            flight_direction=frame.flight_direction,
            type='ARIA',
            metadata=AriaMetadata(),
        )
        for frame in get_frames(
            intersectsWith,  # type: ignore[arg-type] # mypy doesn't recognize this won't be a str
            **options,  # type: ignore[unused-ignore]
        )[:maxResults]
    ]


class FrameQueryError(Exception):
    """Exception for errors with Frame Queries."""
