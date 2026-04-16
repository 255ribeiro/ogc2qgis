# ogc2qgis

Convert OGC Web Services (WMS, WCS, WFS) GetCapabilities XML to QGIS connection configurations.

[![PyPI version](https://badge.fury.io/py/ogc2qgis.svg)](https://badge.fury.io/py/ogc2qgis)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🔄 **Auto-detection**: Automatically identifies service type (WMS, WCS, WFS)
- 📁 **Batch processing**: Convert multiple capabilities files at once
- 🌐 **Remote fetch**: Download capabilities directly from URLs
- 📦 **Zero dependencies**: Uses only Python standard library
- 🎯 **QGIS ready**: Generates files ready to import into QGIS
- 🗂️ **Layer grouping**: Generates `.qlr` Layer Definition files with WMS/WCS/WFS layers organized in category folders
- 🔍 **Compare tools**: Compare local configs, live services, or server IPs
- 🔧 **CLI & Library**: Use as command-line tool or Python library

## 🚀 Quick Start

### Installation

```bash
pip install ogc2qgis
```

### Command Line Usage

```bash
# Convert local file
ogc2qgis convert capabilities.xml

# Fetch and convert from URL
ogc2qgis fetch https://geoservicos.inde.gov.br/geoserver/BAPSalvador/ows

# Process multiple files
ogc2qgis convert ows.xml ows_wcs.xml ows_wfs.xml

# Specify output directory and filename prefix
ogc2qgis convert capabilities.xml -o /path/to/output -p myserver
```

### Python Library Usage

```python
from ogc2qgis import parse_capabilities, fetch_and_convert

# Parse local file
configs = parse_capabilities('capabilities.xml')
# Returns: {'wms': WMSParser, 'wcs': None, 'wfs': None}

# Fetch from URL
results = fetch_and_convert('https://servidor.com/ows')

# Save connection XML
if configs['wms']:
    configs['wms'].save('wms2qgis.xml')

# Save WFS as grouped layer definition (.qlr)
if configs['wfs']:
    configs['wfs'].save_qlr('wfs2qgis.qlr')
```

## 📖 Documentation

### Supported Services

- **WMS** (Web Map Service) 1.3.0 — Map visualization
- **WCS** (Web Coverage Service) 1.1.x / 2.0.x — Raster data download
- **WFS** (Web Feature Service) 1.x / 2.0 — Vector data access

### Output Files

Output filenames are derived from the input filename (or URL path segment):

| Input | Output files |
| --- | --- |
| `ogc2qgis convert capabilities.xml` | `capabilities_wms2qgis.xml` |
| `ogc2qgis fetch .../BAPSalvador/ows` | `ows_wms2qgis.xml`, `ows_wcs2qgis.xml`, `ows_wfs2qgis.xml`, `ows_wfs2qgis.qlr` |

Files are only created when the service type is present in the source — if a server has no WCS data, `*_wcs2qgis.xml` is skipped.

### Import into QGIS

**Connection XML (WMS / WCS / WFS):**

1. Go to **Settings → Options → System**
2. In **Service Connections**, click **Import**
3. Select the generated `*_wms2qgis.xml` / `*_wcs2qgis.xml` / `*_wfs2qgis.xml`

**Grouped Layer Definition (WMS / WCS / WFS — requires `--qlr-include` or `--qlr-only`):**

Option A — drag and drop the `.qlr` file onto the QGIS layer panel or map canvas.

Option B — menu:

1. Go to **Layer → Add Layer → Add from Layer Definition File...**
2. Select the generated `*_wms2qgis.qlr` / `*_wcs2qgis.qlr` / `*_wfs2qgis.qlr`
3. All layers are added to the map, pre-organized in category folders

## 🔧 Advanced Usage

### CLI Options

```text
ogc2qgis convert FILES... [-o DIR] [-p PREFIX] [--qlr-include | --qlr-only] [-v]
ogc2qgis fetch URL        [-o DIR] [-p PREFIX] [--qlr-include | --qlr-only] [-v]
ogc2qgis compare A B      [--comp_web] [--comp_ip] [--service-type wms|wcs|wfs]
```

#### `convert`

| Option | Description |
| --- | --- |
| `-o, --output-dir PATH` | Output directory (default: current directory) |
| `-p, --prefix TEXT` | Filename prefix (default: input filename stem) |
| `--qlr-include` | Generate XML connection file **and** `.qlr` layer definition |
| `--qlr-only` | Generate **only** the `.qlr` layer definition (skip XML) |
| `-v, --verbose` | Verbose output |

#### `fetch`

| Option | Description |
| --- | --- |
| `-o, --output-dir PATH` | Output directory (default: current directory) |
| `-p, --prefix TEXT` | Filename prefix (default: last URL path segment) |
| `--qlr-include` | Generate XML connection file **and** `.qlr` layer definition |
| `--qlr-only` | Generate **only** the `.qlr` layer definition (skip XML) |
| `-v, --verbose` | Verbose output |

#### `compare`

| Option | Description |
| --- | --- |
| *(no flag)* | Compare two local QGIS config XML files |
| `--comp_web` | Fetch both URLs and compare by reported server URL, service name, and layer set |
| `--comp_ip` | Compare by resolving hostnames to IP addresses |
| `--service-type` | Force a service type for `--comp_web` (default: auto-detect) |

```bash
# XML only (default)
ogc2qgis fetch https://server.com/ows

# XML + .qlr
ogc2qgis fetch https://server.com/ows --qlr-include

# .qlr only (no XML)
ogc2qgis fetch https://server.com/ows --qlr-only

# Compare two local config files
ogc2qgis compare old_wfs.xml new_wfs.xml

# Compare two live services (fetches GetCapabilities from both)
ogc2qgis compare --comp_web https://server-a.com/ows https://server-b.com/ows

# Compare by IP (DNS resolution)
ogc2qgis compare --comp_ip https://server-a.com/ows https://server-b.com/ows

# Force service type for web comparison
ogc2qgis compare --comp_web --service-type wfs https://a.com/ows https://b.com/ows
```

**`--comp_web` verdicts:**

| Verdict | Meaning |
| --- | --- |
| `identical` | Same reported server URL, name, and complete layer set |
| `same_server` | Same reported URL but different name or layers |
| `different` | Different servers |

**`--comp_ip` verdicts:**

| Verdict | Meaning |
| --- | --- |
| `identical` | Same hostname and same resolved IPs |
| `same_host` | Identical hostname |
| `same_ip` | Different hostnames but share a common IP |
| `different` | Hostnames resolve to different IPs |

### Library API

```python
from ogc2qgis import (
    WMSParser, WCSParser, WFSParser,
    WFSQLRWriter,
    parse_capabilities, detect_service_type, fetch_and_convert,
    compare_configs, compare_web, compare_ip,
)

# Parse any capabilities file (auto-detects type)
configs = parse_capabilities('capabilities.xml')

# WFS: save connection XML + grouped layer definition
parser = configs['wfs']
if parser:
    parser.save('wfs2qgis.xml')
    parser.save_qlr('wfs2qgis.qlr', group_name='My WFS Server')

# Compare local configs
result = compare_configs('file1.xml', 'file2.xml')
print(result['verdict'])        # 'identical' | 'partial' | ...

# Compare live services
result = compare_web(
    'https://server-a.com/ows',
    'https://server-b.com/ows',
    service_type='wfs',         # optional
)
print(result['verdict'])        # 'identical' | 'same_server' | 'different'
print(result['layer_overlap_pct'])

# Compare by IP
result = compare_ip('https://server-a.com/ows', 'https://server-b.com/ows')
print(result['same_ip'])        # True / False
print(result['common_ips'])     # ['192.168.1.1', ...]
```

### Layer Grouping (`.qlr`)

`.qlr` files can be generated for all three service types using `--qlr-include` or `--qlr-only`.
Layers are automatically grouped into category folders based on their title pattern.
The pattern `N - CODE description` (e.g. `3 - CBGE 1.1 Passeio`) extracts `CBGE` as the folder name.
When no pattern is detected, layers are placed flat under the top-level group.

| Service | Layer type | Grouping |
| --- | --- | --- |
| WFS | vector | category codes from titles (e.g. CBGE, HID, TRA) |
| WMS | raster | category codes from titles (same pattern, when present) |
| WCS | raster | category codes from titles (same pattern, when present) |

```python
from ogc2qgis.parsers.qlr import WFSQLRWriter, WMSQLRWriter, WCSQLRWriter

# WFS
WFSQLRWriter(url='https://server.com/wfs', service_name='My WFS',
             features=[{'name': 'ws:rivers', 'title': '1 - HID Rivers'}]).save('wfs.qlr')

# WMS
WMSQLRWriter(url='https://server.com/wms', service_name='My WMS',
             layers=[{'name': 'layer1', 'title': '2 - TRA Road'}]).save('wms.qlr')

# WCS
WCSQLRWriter(url='https://server.com/wcs', service_name='My WCS',
             coverages=[{'identifier': 'mds_01', 'title': 'MDS Lote 01'}]).save('wcs.qlr')
```

## 🌐 Real World Example

```bash
ogc2qgis fetch https://geoservicos.inde.gov.br/geoserver/BAPSalvador/ows

# Output:
# ✓ ows_wms2qgis.xml  (111 layers)
# ✓ ows_wcs2qgis.xml  (7 coverages)
# ✓ ows_wfs2qgis.xml  (server connection)
# ✓ ows_wfs2qgis.qlr  (84 layers in 14 category folders)
#
# Import connections: Settings → Options → System → Service Connections → Import
# Import grouped WFS: Layer → Add from Layer Definition File (.qlr)
```

## 🧪 Development

```bash
# Clone repository
git clone https://github.com/ogc2qgis/ogc2qgis.git
cd ogc2qgis

# Install with Poetry
poetry install

# Run tests
poetry run pytest

# Format code
poetry run black src/

# Lint
poetry run ruff src/
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 🔗 Links

- **PyPI**: [pypi.org/project/ogc2qgis](https://pypi.org/project/ogc2qgis/)
- **Source Code**: [github.com/255ribeiro/ogc2qgis](https://github.com/255ribeiro/ogc2qgis)
- **Issue Tracker**: [github.com/255ribeiro/ogc2qgis/issues](https://github.com/255ribeiro/ogc2qgis/issues)
- **QGIS**: [qgis.org](https://qgis.org/)
- **OGC Standards**: [ogc.org](https://www.ogc.org/)
