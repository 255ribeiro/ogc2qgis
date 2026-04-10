"""
Example: Using ogc2qgis as a Python library
"""

from ogc2qgis import WMSParser, WCSParser, parse_capabilities, fetch_and_convert

# Example 1: Parse specific service type
print("Example 1: Parse WMS file")
wms_parser = WMSParser('capabilities_wms.xml')
print(f"  Service: {wms_parser.service_name}")
print(f"  URL: {wms_parser.server_url}")
print(f"  Layers: {len(wms_parser.layers)}")

# Save QGIS config
wms_parser.save('output_wms.xml')
print("  ✓ Saved to output_wms.xml\n")

# Example 2: Auto-detect service type
print("Example 2: Auto-detect and parse")
configs = parse_capabilities('capabilities.xml')

if configs['wms']:
    print(f"  WMS detected: {configs['wms'].service_name}")
    configs['wms'].save('qgis_wms_connections.xml')

if configs['wcs']:
    print(f"  WCS detected: {configs['wcs'].service_name}")
    configs['wcs'].save('qgis_wcs_connections.xml')

if configs['wfs']:
    print(f"  WFS detected: {configs['wfs'].service_name}")
    configs['wfs'].save('qgis_wfs_connections.xml')

print()

# Example 3: Fetch from URL
print("Example 3: Fetch from remote server")
results = fetch_and_convert(
    'https://geoservicos.inde.gov.br/geoserver/BAPSalvador/ows',
    output_dir='./configs'
)

for service_type, filepath in results.items():
    if filepath:
        print(f"  ✓ {service_type.upper()}: {filepath}")
    else:
        print(f"  ✗ {service_type.upper()}: not available")

print("\n✨ Done! Import the XML files into QGIS.")
