import shapely

from asf_enumeration.s1_burst import get_slc_burst_ids

from .Frame import Frame, Options, AriaMetadata
from .aria_s1_gunw import get_frames as get_aria_frames
from asf_search import validate_wkt


def get_frames(
    type: str,
    intersectsWith: str | shapely.geometry.base.BaseGeometry,
    maxResults: int = 250,
    options: Options | None = None,
) -> list[Frame] | None:
    if type == 'BURST':
        return get_slc_burst_ids(intersectsWith=intersectsWith, maxResults=maxResults, *options)
    elif type == 'ARIA':
        return get_aria_frame_ids(intersectsWith, options)
    elif type == 'NISAR':
        return
    pass


def get_aria_frame_ids(
    intersectsWith: shapely.geometry.base.BaseGeometry | str, options: Options
) -> list[Frame]:
    if isinstance(intersectsWith, str):
        intersectsWith, _, __ = validate_wkt(intersectsWith)
    return [
        Frame(str(frame.id), frame.polygon, frame.flight_direction, 'ARIA', AriaMetadata())
        for frame in get_aria_frames(intersectsWith, *options)
    ]
