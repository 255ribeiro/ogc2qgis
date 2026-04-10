#!/bin/bash
# Examples of using ogc2qgis CLI

echo "=== ogc2qgis CLI Examples ==="
echo

# Example 1: Convert single file
echo "Example 1: Convert single file"
ogc2qgis convert capabilities.xml
echo

# Example 2: Convert multiple files
echo "Example 2: Convert multiple files"
ogc2qgis convert ows.xml ows_wcs.xml ows_wfs.xml
echo

# Example 3: Custom output directory
echo "Example 3: Custom output directory"
ogc2qgis convert capabilities.xml -o ./my_configs
echo

# Example 4: Verbose output
echo "Example 4: Verbose output"
ogc2qgis convert capabilities.xml -v
echo

# Example 5: Fetch from URL
echo "Example 5: Fetch from URL"
ogc2qgis fetch https://geoservicos.inde.gov.br/geoserver/BAPSalvador/ows
echo

# Example 6: Fetch to custom directory
echo "Example 6: Fetch to custom directory"
ogc2qgis fetch https://geoservicos.inde.gov.br/geoserver/BAPSalvador/ows -o ./inde_configs
echo

# Example 7: Help
echo "Example 7: Show help"
ogc2qgis --help
echo

# Example 8: Version
echo "Example 8: Show version"
ogc2qgis --version
echo

echo "✨ Done! Check the generated XML files."
