"""For Sentinel-1 SLC Burst frame id querying."""

import asf_search as asf
import shapely

from .frame import BurstMetadata, Frame, Options


def get_slc_burst_frame_ids(
    intersectsWith: str | shapely.geometry.base.BaseGeometry,
    options: Options,
    maxResults: int = 250,
) -> list[Frame]:
    """Gets SLC Bursts frames over a given AOI from CMR.

    Args:
        intersectsWith: the AOI to query with
        options: Various options relevant to query burst frames (see `BurstOptions`) for more
        maxResults: How many frames to limit results to

    """
    burstmap = 'Sentinel-1_Burst_Map'

    # TODO: remove this when asf-search actually supports taking BaseGeometry objects
    if intersectsWith and isinstance(intersectsWith, shapely.geometry.base.BaseGeometry):
        intersectsWith = intersectsWith.wkt

    opts = asf.ASFSearchOptions(
        intersectsWith=intersectsWith,
        flightDirection=options.get('flight_direction'),
        relativeOrbit=options.get('path'),
        maxResults=maxResults,
    )
    if (subswath := options.get('subswath')) is not None:
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
