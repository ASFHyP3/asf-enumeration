"""For Sentinel-1 SLC Burst frame id querying."""

import asf_search as asf
import shapely

from .frame import BurstMetadata, Frame


def get_slc_burst_ids(
    intersectsWith: str | shapely.geometry.base.BaseGeometry,
    flight_direction: str | None = None,
    path: int | None = None,
    subswath: str | None = None,
    maxResults: int = 250,
) -> list[Frame]:
    """Gets SLC Bursts frames over a given AOI from CMR.

    Args:
        intersectsWith: the AOI to query with
        flight_direction: the flight direction of the frame(s) (`ASCENDING` or `DESCENDING`)
        path: the path (`relativeOrbit`) of the frame(s)
        subswath: the subswath (ex: 'EW2')
        maxResults: How many frames to limit results to

    """
    kwargs = locals()
    burstmap = 'Sentinel-1_Burst_Map'

    # TODO: remove this when asf-search actually supports taking BaseGeometry objects
    if intersectsWith and isinstance(intersectsWith, shapely.geometry.base.BaseGeometry):
        intersectsWith = intersectsWith.wkt

    opts = asf.ASFSearchOptions(
        intersectsWith=intersectsWith,
        flightDirection=flight_direction,
        relativeOrbit=path,
        maxResults=maxResults,
    )
    if subswath is not None:
        opts.cmr_keywords = [('attribute[]', f'string,SUBSWATH_NAME,{subswath}')]

    return [
        Frame(
            id=product.properties['fileID'],
            polygon=product.geometry,
            flight_direction=product.properties['flightDirection'],
            type='BURST',
            metadata=BurstMetadata(),
        )
        for product in asf.search(shortName=burstmap, opts=opts)
    ]
