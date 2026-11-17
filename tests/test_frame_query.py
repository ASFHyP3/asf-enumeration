import pytest
import shapely

import asf_enumeration.frame
import asf_enumeration.frame_query


def test_get_frames():
    wkt = 'POLYGON((-128.0401 57.1054,-127.7544 57.1054,-127.7544 57.2034,-128.0401 57.2034,-128.0401 57.1054))'
    search_polygon = shapely.from_wkt(wkt)

    frames = asf_enumeration.frame_query.get_frame_ids(
        type='SLC-BURST', intersectsWith=wkt, maxResults=250, options=None
    )
    assert len(frames) == 27

    frames_max_results = asf_enumeration.frame_query.get_frame_ids(
        type='SLC-BURST', intersectsWith=wkt, maxResults=10, options=None
    )
    assert len(frames_max_results) == 10

    frames = asf_enumeration.frame_query.get_frame_ids(
        type='SLC-BURST',
        intersectsWith=search_polygon,
        maxResults=250,
        options=asf_enumeration.frame.BurstOptions(flight_direction='ASCENDING', subswath=None, path=None),
    )
    assert len(frames) == 13

    frames = asf_enumeration.frame_query.get_frame_ids(
        type='SLC-BURST',
        intersectsWith='POINT(-88.4131 -74.8288)',
        maxResults=250,
        options=asf_enumeration.frame.BurstOptions(flight_direction='ASCENDING', subswath='IW3', path=50),
    )
    assert len(frames) == 1

    wkt = 'POLYGON((-128.0401 57.1054,-127.7544 57.1054,-127.7544 57.2034,-128.0401 57.2034,-128.0401 57.1054))'
    search_polygon = shapely.from_wkt(wkt)

    frames = asf_enumeration.frame_query.get_frame_ids(
        type='ARIA S1 GUNW',
        intersectsWith=search_polygon,
    )
    assert len(frames) == 8

    frames = asf_enumeration.frame_query.get_frame_ids(
        type='ARIA S1 GUNW',
        intersectsWith=search_polygon,
    )
    assert len(frames) == 8

    all_filters = asf_enumeration.frame_query.get_frame_ids(
        type='ARIA S1 GUNW',
        intersectsWith=search_polygon,
        options=asf_enumeration.frame.AriaOptions(flight_direction='ASCENDING', path=35),
    )
    assert len(all_filters) == 2

    all_filters_max_results = asf_enumeration.frame_query.get_frame_ids(
        type='ARIA S1 GUNW',
        intersectsWith=search_polygon,
        maxResults=1,
        options=asf_enumeration.frame.AriaOptions(flight_direction='ASCENDING', path=35),
    )
    assert len(all_filters_max_results) == 1

    with pytest.raises(asf_enumeration.frame_query.FrameQueryError):
        asf_enumeration.frame_query.get_frame_ids(
            type='INVALID_TYPE',
            intersectsWith=search_polygon,
        )

    with pytest.raises(asf_enumeration.frame_query.FrameQueryError):
        asf_enumeration.frame_query.get_frame_ids(
            type='ARIA S1 GUNW',
            intersectsWith=None,  # type: ignore[arg-type]
        )
