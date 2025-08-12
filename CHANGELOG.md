# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [PEP 440](https://www.python.org/dev/peps/pep-0440/)
and uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0]

### Added
- Add property `Sentinel1Acquisition.frame_coverage`
- Add `min_frame_coverage` parameter to `aria_s1_gunw.get_acquisitions` to filter by frame overlap

## [0.2.0]

### Added
- Added a new function `aria_s1_gunw.get_product` for getting an ARIA product if it exists:
  ```
  get_product(
      reference_date: datetime.date | str, secondary_date: datetime.date | str, frame_id: int
  ) -> asf.ASFProduct | None
  ```

### Changed
- The interface for `aria_s1_gunw.product_exists` has changed from:
  ```
  product_exists(frame: int | AriaFrame, reference_date: datetime.date, secondary_date: datetime.date) -> bool
  ```
  to:
  ```
  product_exists(reference_date: datetime.date | str, secondary_date: datetime.date | str, frame_id: int) -> bool
  ```
  Fixes https://github.com/ASFHyP3/asf-enumeration/issues/10

### Fixed
- `aria_s1_gunw.AriaFrame.does_intersect` now returns a `bool` rather than a `numpy.bool` so as to match the return type annotation.

## [0.1.0]

### Added
- `asf_enumeration` module
   - contains `aria_s1_gunw` module
      - `AriaFrame`, `Sentinel1Acquisition`, `get_frames`, `get_frame`, `get_acquisitions`, `get_acquisition`, `product_exists`
