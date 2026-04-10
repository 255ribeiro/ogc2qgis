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

# Specify output directory
ogc2qgis convert capabilities.xml -o /path/to/output
```

### Python Library Usage

```python
from ogc2qgis import parse_capabilities, fetch_and_convert

# Parse local file
configs = parse_capabilities('capabilities.xml')
# Returns: {'wms': QGISConfig, 'wcs': None, 'wfs': None}

# Fetch from URL
configs = fetch_and_convert('https://servidor.com/ows')

# Save to file
if configs['wms']:
    configs['wms'].save('qgis_wms_connections.xml')
```

## 📖 Documentation

### Supported Services

- **WMS** (Web Map Service) - Map visualization
- **WCS** (Web Coverage Service) - Raster data download
- **WFS** (Web Feature Service) - Vector data access

### Output Files

The tool generates QGIS-compatible XML files:
- `qgis_wms_connections.xml` - WMS connections
- `qgis_wcs_connections.xml` - WCS connections
- `qgis_wfs_connections.xml` - WFS connections

### Import into QGIS

1. Open QGIS
2. Go to **Settings** → **Options** → **System**
3. In **Service Connections** section, click **Import**
4. Select the generated XML file(s)
5. Done! Servers appear in your connection lists

## 🔧 Advanced Usage

### CLI Options

```bash
ogc2qgis convert --help

Usage: ogc2qgis convert [OPTIONS] FILES...

Options:
  -o, --output-dir PATH  Output directory for generated files
  -p, --prefix TEXT      Prefix for output filenames
  -v, --verbose          Verbose output
  --help                 Show this message and exit
```

### Library API

```python
from ogc2qgis.parsers import WMSParser, WCSParser, WFSParser

# Parse WMS
parser = WMSParser('ows.xml')
print(f"Service: {parser.service_name}")
print(f"URL: {parser.server_url}")
print(f"Layers: {len(parser.layers)}")

# Generate config
config = parser.to_qgis_config()
config.save('output.xml')

# Auto-detect service type
from ogc2qgis.core import detect_service_type
service_type = detect_service_type('capabilities.xml')  # Returns 'wms', 'wcs', 'wfs', or None
```

## 🌐 Real World Example

```bash
# INDE Brazil - Salvador Geographic Data
ogc2qgis fetch https://geoservicos.inde.gov.br/geoserver/BAPSalvador/ows

# Output:
# ✅ Downloaded WMS capabilities (111 layers)
# ✅ Downloaded WCS capabilities (7 coverages)
# ✅ Generated qgis_wms_connections.xml
# ✅ Generated qgis_wcs_connections.xml
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

- **PyPI**: https://pypi.org/project/ogc2qgis/
- **Source Code**: https://github.com/ogc2qgis/ogc2qgis
- **Issue Tracker**: https://github.com/ogc2qgis/ogc2qgis/issues
- **QGIS**: https://qgis.org/
- **OGC Standards**: https://www.ogc.org/

## 📊 Status

This project is actively maintained. If you encounter any issues or have feature requests, please open an issue on GitHub.
