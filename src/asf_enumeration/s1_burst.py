import asf_search as asf
import shapely

from asf_enumeration.Frame import BurstMetadata, Frame


def get_slc_burst_ids(
    intersectsWith: str | shapely.geometry.base.BaseGeometry,
    flightDirection: str | None = None,
    path: int | None = None,
    subswath: int | None = None,
    maxResults: int = 250,
) -> list[Frame]:
    """Gets SLC Bursts frames over a given AOI from CMR."""
    kwargs = locals()
    burstmap = 'Sentinel-1_Burst_Map'
    opts = asf.ASFSearchOptions(
        intersectsWith=intersectsWith,
        flightDirection=flightDirection,
        pathNumber=path,
        maxResults=maxResults,
    )
    if subswath is not None:
        opts.cmr_keywords = [('attribute[]', f'string,SUBSWATH_NAME,{subswath}')]

    return [
        Frame(
            id=product.properties['fileID'],
            polygon=product.geometry,
            flightDirection=product.properties['flightDirection'],
            type='BURST',
            metadata=BurstMetadata(),
        )
        for product in asf.search(shortName=burstmap, opts=opts)
    ]
