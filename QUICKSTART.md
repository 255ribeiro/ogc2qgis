# Quick Start Guide

## Installation

```bash
pip install ogc2qgis
```

## Usage Examples

### 1. Convert Local File

```bash
ogc2qgis convert capabilities.xml
```

### 2. Fetch from URL

```bash
ogc2qgis fetch https://geoservicos.inde.gov.br/geoserver/BAPSalvador/ows
```

### 3. Multiple Files

```bash
ogc2qgis convert *.xml -o ./output
```

### 4. Python Library

```python
from ogc2qgis import parse_capabilities

# Parse file
configs = parse_capabilities('capabilities.xml')

# Save QGIS config
if configs['wms']:
    configs['wms'].save('qgis_wms_connections.xml')
```

## Importing into QGIS

1. Open QGIS
2. Go to: **Settings → Options → System**
3. Click **Service Connections → Import**
4. Select the generated XML file(s)
5. Done!

## Development

### Setup

```bash
git clone https://github.com/ogc2qgis/ogc2qgis.git
cd ogc2qgis
poetry install
```

### Run Tests

```bash
poetry run pytest
```

### Build Package

```bash
poetry build
```

### Publish to PyPI

```bash
poetry publish
```

## Common Issues

**Q: File not generating?**
A: Check that input file is valid OGC GetCapabilities XML

**Q: Service not detected?**
A: Ensure XML has proper WMS/WCS/WFS root element

**Q: Can't import into QGIS?**
A: Verify QGIS version is 3.x and file is in correct location

## Getting Help

- 📖 Full documentation: https://github.com/ogc2qgis/ogc2qgis
- 🐛 Report issues: https://github.com/ogc2qgis/ogc2qgis/issues
- 💬 Discussions: https://github.com/ogc2qgis/ogc2qgis/discussions
