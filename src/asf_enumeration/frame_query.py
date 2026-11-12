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
        type: Type of frames to query. Either 'BURST', 'ARIA', or 'NISAR'
        intersectsWith: the AOI to query with
        maxResults: How many frames to limit results to
        options: Relevant options for different frame types
    """
    if options is None:
        options = {}

    if intersectsWith and not isinstance(intersectsWith, str):
        intersectsWith = intersectsWith.wkt

    if type == 'BURST':
        return get_slc_burst_ids(
            intersectsWith,
            **options,  # type: ignore (linter hates spreading TypedDicts that are part of union types)
            maxResults=maxResults,
        )
    elif type == 'ARIA':
        return _get_aria_frame_ids(intersectsWith, options)

    raise FrameQueryError(
        f'Unsupported argument passed to `type`. Expected `BURST` or `ARIA`. Got `{type}`'
    )


def _get_aria_frame_ids(
    intersectsWith: shapely.geometry.base.BaseGeometry | str, options: Options
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
            intersectsWith,
            **options,  # type: ignore (linter hates spreading TypedDicts that are part of union types)
        )
    ]


class FrameQueryError(Exception):
    """Exception for errors with Frame Queries."""
