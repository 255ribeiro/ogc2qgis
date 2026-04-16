# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **`.qlr` Layer Definition for all service types**: WMS, WCS, and WFS can now generate
  QGIS Layer Definition files with layers pre-organized in category folders. Categories
  are detected automatically from title patterns (`N - CODE description`, e.g.
  `3 - CBGE 1.1 Passeio`). Import via **Layer → Add from Layer Definition File** in QGIS.
  The `.qlr` is self-contained — no prior server configuration needed.
- **`--qlr-include`** flag on `convert` and `fetch`: generate both XML connection file
  and `.qlr` layer definition.
- **`--qlr-only`** flag on `convert` and `fetch`: generate only the `.qlr` layer
  definition, skip XML connection file. The two flags are mutually exclusive.
- **`WMSQLRWriter`**, **`WCSQLRWriter`**, **`WFSQLRWriter`**: public classes in
  `ogc2qgis.parsers.qlr` for building `.qlr` files programmatically; also accessible
  via `WMSParser.save_qlr()`, `WCSParser.save_qlr()`, `WFSParser.save_qlr()`.
- **`compare --comp_web`**: new CLI flag to compare two live OGC service URLs by fetching
  their GetCapabilities and comparing reported server URL, service name, and layer set.
  Returns verdicts `identical`, `same_server`, or `different`.
- **`compare --comp_ip`**: new CLI flag to compare two URLs by resolving their hostnames
  to IP addresses via DNS. Returns verdicts `identical`, `same_host`, `same_ip`,
  or `different`.
- **`compare_web(url1, url2)`**: new library function for programmatic live-service comparison.
- **`compare_ip(url1, url2)`**: new library function for programmatic IP-based comparison.
- **`--service-type`** option on `compare --comp_web` to force a specific OGC service type
  instead of auto-detecting.

### Fixed

- **WCS URL extraction** (`wcs.py`): parser now handles WCS 2.0.x responses
  (`ows="http://www.opengis.net/ows/2.0"`, `wcs="http://www.opengis.net/wcs/2.0"`).
  Previously only WCS 1.1.x was supported, causing empty URLs on GeoServer instances.
- **WCS coverage identifiers**: WCS 2.0 uses `<wcs:CoverageId>` instead of `<wcs:Identifier>`;
  both are now handled.
- **WFS URL extraction** (`wfs.py`): parser now handles WFS 2.0.0 responses
  (`ows="http://www.opengis.net/ows/1.1"`, `wfs="http://www.opengis.net/wfs/2.0"`).
  Previously used unversioned namespaces, causing empty URLs on WFS 2.0 servers.
- Both parsers now include a `{*}` namespace-wildcard fallback (Python 3.8+) as a last
  resort, making them resilient to future namespace variants.

### Changed

- **Output filename format**: generated files are now named `{stem}_{type}2qgis.xml`
  (e.g. `capabilities_wms2qgis.xml`) instead of the previous `qgis_{type}_connections.xml`.
  For `fetch`, the stem is derived from the last URL path segment.
- **Skip empty outputs**: a service-type output file is no longer created when the parser
  finds no meaningful data (empty URL and no layers / coverages / features).
- **`--prefix` / `-p`** option on `convert` and `fetch` is now optional (default: input
  filename stem or URL path segment). When provided it overrides the automatic stem.

## [0.1.0] - 2025-04-10

- Initial release
- WMS GetCapabilities parser
- WCS GetCapabilities parser (1.1.x)
- WFS GetCapabilities parser (1.x)
- Auto-detection of service type
- CLI tool with `convert` and `fetch` commands
- `compare` command for comparing local QGIS config files
- `compare_configs()` library function
- Python library API
- QGIS-compatible XML output (`qgsWMSConnections`, `qgsWCSConnections`, `qgsWFSConnections`)
- Zero dependencies (stdlib only)
- Support for Python 3.8+
- Comprehensive test suite
- CI/CD with GitHub Actions
- Documentation and examples

[Unreleased]: https://github.com/255ribeiro/ogc2qgis/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/255ribeiro/ogc2qgis/releases/tag/v0.1.0
