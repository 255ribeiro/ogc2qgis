# ✅ Compare Command Added to CLI

## New CLI Command

The `compare` command is now available in the ogc2qgis CLI tool!

## Usage

```bash
ogc2qgis compare <file1.xml> <file2.xml>
```

## Examples

### Example 1: Compare two WMS configs
```bash
ogc2qgis compare qgis_wms_connections_old.xml qgis_wms_connections_new.xml
```

**Output:**
```
======================================================================
QGIS Configuration Comparison
======================================================================

File 1: qgis_wms_connections_old.xml
File 2: qgis_wms_connections_new.xml

Service Type: WMS vs WMS

Connections:
  File 1: 1 server(s)
  File 2: 1 server(s)

✅ Common Servers: 1

Common server details:
  • https://geoservicos.inde.gov.br/geoserver/bapsalvador/ows
    File 1 name: GeoServer INDE
    File 2 name: GeoServer INDE

======================================================================
✅ IDENTICAL: Both files point to the exact same server(s)
```

### Example 2: Help
```bash
ogc2qgis compare --help
```

## Exit Codes

The compare command returns different exit codes:

- **0** - Files are identical (same servers)
- **1** - Partial match (some common servers)
- **2** - No match (completely different servers)

## Use in Scripts

```bash
#!/bin/bash

# Check if configs match
if ogc2qgis compare staging.xml production.xml; then
    echo "✅ Production matches staging"
else
    echo "⚠️ Configurations differ!"
    exit 1
fi
```

## All CLI Commands

Now the ogc2qgis CLI has 3 commands:

1. **`convert`** - Convert GetCapabilities files
   ```bash
   ogc2qgis convert capabilities.xml
   ```

2. **`fetch`** - Fetch from URL and convert
   ```bash
   ogc2qgis fetch https://server.com/ows
   ```

3. **`compare`** - Compare two QGIS configs ✨ **NEW**
   ```bash
   ogc2qgis compare file1.xml file2.xml
   ```

## See Also

- Library usage: `from ogc2qgis import compare_configs`
- Full documentation: `ogc2qgis --help`
