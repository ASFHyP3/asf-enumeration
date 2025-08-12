"""Module for enumerating inputs for ARIA S1 GUNW products."""

import datetime
import importlib.resources
import json
import typing
from collections import defaultdict
from dataclasses import dataclass

import asf_search as asf
import shapely
from shapely import ops


FlightDirections = typing.Literal['ASCENDING', 'DESCENDING']


@dataclass(frozen=True)
class AriaFrame:
    """Class for representing an ARIA frame.

    Args:
        id: ID of the ARIA frame
        path: path the frame is on
        flight_direction: flight direction of the burst
        polygon: shapely polygon of the frame geometry
    """

    id: int
    path: int
    flight_direction: FlightDirections
    polygon: shapely.Polygon

    def does_intersect(self, geometry: shapely.Geometry) -> bool:
        """Check if geometry intersects ARIA frame.

        Args:
            geometry: shapely geometry to check frames against

        Returns:
            does_intersect: if the frame instersects the geometry
        """
        return bool(shapely.intersects(self.polygon, geometry))

    @property
    def wkt(self) -> str:
        """Get the wkt of the frames polygon.

        Returns:
            wkt: The wkt of the ARIA frame
        """
        return shapely.to_wkt(self.polygon)


@dataclass(frozen=True)
class Sentinel1Acquisition:
    """Class respresenting a Sentinel-1 acquisition over a given ARIA frame.

    Args:
         date: the date of the acquisition
         frame: ARIA frame the the acquisition covers
         products: list of Sentinel-1 SLC's from the acquisition
    """

    date: datetime.date
    frame: AriaFrame
    products: list[asf.ASFProduct]

    @property
    def frame_coverage(self) -> float:
        """Get the ratio of coverage of the acquisition with the ARIA frame.

        Returns:
            frame_coverage: coverage ratio with ARIA frame
        """
        slc_shapes = [shapely.geometry.shape(slc.geojson()['geometry']) for slc in self.products]
        acquisition_footprint = ops.unary_union(slc_shapes)
        footprint_intersection = self.frame.polygon.intersection(acquisition_footprint)

        return footprint_intersection.area / self.frame.polygon.area


class AriaEnumerationError(Exception):
    """Exception for errors with ARIA S1 GUNW enumeration."""

    pass


def _validate_frame_id(frame_id: int) -> None:
    if frame_id not in FRAMES_BY_ID:
        raise AriaEnumerationError(f'Frame ID is out of range [0, 27397] given {frame_id}')


def _validate_flight_direction(flight_direction: FlightDirections | None) -> None:
    if flight_direction and flight_direction.upper() not in typing.get_args(FlightDirections):
        raise AriaEnumerationError('Invalid flight direction, must be either "ASCENDING" or "DESCENDING"')


def _load_aria_frames_by_id() -> dict[int, AriaFrame]:
    frames_by_id = {}

    with importlib.resources.path('asf_enumeration.frame_maps', 'aria_frames.geojson') as frame_file:
        frames = json.loads(frame_file.read_text())

    for frame in frames['features']:
        props = frame['properties']

        aria_frame = AriaFrame(
            id=props['id'],
            path=props['path'],
            flight_direction=props['dir'],
            polygon=shapely.Polygon(frame['geometry']['coordinates'][0]),
        )

        frames_by_id[aria_frame.id] = aria_frame

    return frames_by_id


FRAMES_BY_ID = _load_aria_frames_by_id()


def get_frames(
    geometry: shapely.Geometry | None = None, flight_direction: FlightDirections | None = None, path: int | None = None
) -> list[AriaFrame]:
    """Get all ARIA frames that match filter parameters.

    Args:
        geometry: get all frames intersecting polygon
        flight_direction: flight direction to filter by
        path: path to filter frames

    Returns:
        aria_frames: list of ARIA frames
    """
    _validate_flight_direction(flight_direction)
    aria_frames = []

    for frame in FRAMES_BY_ID.values():
        if flight_direction and flight_direction.upper() != frame.flight_direction:
            continue

        if path and path != frame.path:
            continue

        if geometry and not frame.does_intersect(geometry):
            continue

        aria_frames.append(frame)

    return aria_frames


def get_frame(frame_id: int) -> AriaFrame:
    """Get a single ARIA frame based on it's ID.

    Args:
        frame_id: ARIA frame id

    Returns:
        aria_frame: the ARIA frame with the given ID
    """
    _validate_frame_id(frame_id)
    return FRAMES_BY_ID[frame_id]


# Keep min_frame_coverage up to date with the hyp3 job spec
# https://github.com/ASFHyP3/hyp3/blob/1c033fb0d3a20b99082a5ca631531f2b68aa727f/job_spec/ARIA_S1_GUNW.yml#L49-L50
def get_acquisitions(frame: int | AriaFrame, min_frame_coverage: float | None = 0.9) -> list[Sentinel1Acquisition]:
    """Get all the possible Sentinel-1 acquisitions over a given ARIA frame ID.

    Args:
        frame: the ARIA frame ID or frame object to get the acquisitions from
        min_frame_coverage: the amount the acquisition needs to overlap with the ARIA frame

    Returns:
        acquisitions: All the Sentinel-1 acquisitions for a given ARIA frame
    """
    if isinstance(frame, int):
        frame = get_frame(frame)

    granules = _get_granules_for(frame)
    acquisitions = _get_acquisitions_from(granules, frame)

    if min_frame_coverage is not None:
        acquisitions = [acquisition for acquisition in acquisitions if acquisition.frame_coverage >= min_frame_coverage]

    acquisitions.sort(key=lambda group: group.date)
    return acquisitions


def _get_granules_for(frame: AriaFrame, date: datetime.date | None = None) -> asf.ASFSearchResults:
    search_params = {
        'dataset': asf.constants.DATASET.SENTINEL1,
        'platform': ['SA', 'SB'],
        'processingLevel': asf.constants.PRODUCT_TYPE.SLC,
        'beamMode': asf.constants.BEAMMODE.IW,
        'polarization': [asf.constants.POLARIZATION.VV, asf.constants.POLARIZATION.VV_VH],
        'flightDirection': frame.flight_direction,
        'relativeOrbit': frame.path,
        'intersectsWith': frame.wkt,
    }

    if date:
        date_as_datetime = datetime.datetime(year=date.year, month=date.month, day=date.day)
        search_params['start'] = date_as_datetime - datetime.timedelta(minutes=5)
        search_params['end'] = date_as_datetime + datetime.timedelta(days=1, minutes=5)

    results = asf.search(**search_params)

    return results


def _get_acquisitions_from(granules: asf.ASFSearchResults, frame: AriaFrame) -> list[Sentinel1Acquisition]:
    acquisition_groups = defaultdict(list)
    for granule in granules:
        props = granule.properties
        group_id = f'{props["platform"]}_{props["orbit"]}'
        acquisition_groups[group_id].append(granule)

    def get_date_from_group(group: list[asf.ASFProduct]) -> datetime.date:
        return min(_date_from_granule(granule) for granule in group)

    s1_acquisitions = [
        Sentinel1Acquisition(date=get_date_from_group(group), frame=frame, products=[product for product in group])
        for group in acquisition_groups.values()
    ]

    return s1_acquisitions


def get_acquisition(frame: int | AriaFrame, date: datetime.date) -> Sentinel1Acquisition:
    """Get a Sentinel-1 acquisition for a given frame and date.

    Args:
        frame: ARIA frame ID or frame object
        date: date of the acquisition

    Returns:
        acquisition: Sentiel 1 acquisition

    """
    if isinstance(frame, int):
        frame = get_frame(frame)

    products = _get_granules_for(frame, date)
    acquisition = Sentinel1Acquisition(date=date, frame=frame, products=products)

    return acquisition


def product_exists(reference_date: datetime.date | str, secondary_date: datetime.date | str, frame_id: int) -> bool:
    """Check if ARIA product already exists.

    Args:
        reference_date: Reference date of the product as a `datetime.date` object or a date string in ISO format
        secondary_date: Secondary date of the product as a `datetime.date` object or a date string in ISO format
        frame_id: ARIA frame ID

    Returns:
        Whether the product already exists in ASF's archive

    """
    return get_product(reference_date, secondary_date, frame_id) is not None


def get_product(
    reference_date: datetime.date | str, secondary_date: datetime.date | str, frame_id: int
) -> asf.ASFProduct | None:
    """Get the ARIA product for the given parameters, if it exists.

    Args:
        reference_date: Reference date of the product as a `datetime.date` object or a date string in ISO format
        secondary_date: Secondary date of the product as a `datetime.date` object or a date string in ISO format
        frame_id: ARIA frame ID

    Returns:
        The product if it exists, otherwise None.
    """
    if isinstance(reference_date, str):
        reference_date = datetime.date.fromisoformat(reference_date)

    if isinstance(secondary_date, str):
        secondary_date = datetime.date.fromisoformat(secondary_date)

    _validate_frame_id(frame_id)

    date_buffer = datetime.timedelta(days=1)

    results = asf.search(
        dataset=asf.constants.DATASET.ARIA_S1_GUNW,
        frame=frame_id,
        start=reference_date - date_buffer,
        end=reference_date + date_buffer,
    )
    results = [
        result
        for result in results
        if _gunw_dates_match(result.properties['sceneName'], reference_date, secondary_date)
    ]
    if not results:
        return None

    return max(results, key=lambda product: product.meta['revision-date'])


def _gunw_dates_match(granule: str, reference: datetime.date, secondary: datetime.date) -> bool:
    date_strs = granule.split('-')[6].split('_')
    granule_reference, granule_secondary = [
        datetime.datetime.strptime(date_str, '%Y%m%d').date() for date_str in date_strs
    ]

    return granule_reference == reference and granule_secondary == secondary


def _date_from_granule(granule: asf.ASFProduct) -> datetime.date:
    start_time = granule.properties['startTime']
    return datetime.datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S%z').date()
