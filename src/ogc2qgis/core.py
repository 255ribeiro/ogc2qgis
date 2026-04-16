"""Core functionality for detecting and converting OGC services."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Optional, Union
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from ogc2qgis.parsers.wms import WMSParser
from ogc2qgis.parsers.wcs import WCSParser
from ogc2qgis.parsers.wfs import WFSParser


def detect_service_type(xml_file: Union[str, Path]) -> Optional[str]:
    """
    Detect OGC service type from XML file.
    
    Args:
        xml_file: Path to XML capabilities file
        
    Returns:
        Service type ('wms', 'wcs', 'wfs') or None if unknown
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Get tag without namespace
        tag = root.tag.split('}')[-1]
        
        # Detect by root tag
        if 'WMS' in tag or 'WMS_Capabilities' in tag:
            return 'wms'
        elif ('WCS' in tag or 'Capabilities' in tag) and 'wcs' in root.tag.lower():
            return 'wcs'
        elif 'WFS' in tag or 'WFS_Capabilities' in tag:
            return 'wfs'
        
        # Detect by content
        if root.find('.//{http://www.opengis.net/wcs/1.1.1}CoverageSummary') is not None:
            return 'wcs'
        elif root.find('.//{http://www.opengis.net/wms}Layer') is not None or \
             root.find('.//Layer') is not None:
            return 'wms'
        elif root.find('.//{http://www.opengis.net/wfs}FeatureType') is not None or \
             root.find('.//FeatureType') is not None:
            return 'wfs'
        
        return None
    except Exception:
        return None


def parse_capabilities(xml_file: Union[str, Path]) -> Dict[str, Optional[object]]:
    """
    Parse capabilities file and return appropriate parser.
    
    Args:
        xml_file: Path to XML capabilities file
        
    Returns:
        Dict with keys 'wms', 'wcs', 'wfs' containing parser objects or None
    """
    service_type = detect_service_type(xml_file)
    
    result = {'wms': None, 'wcs': None, 'wfs': None}
    
    if service_type == 'wms':
        result['wms'] = WMSParser(xml_file)
    elif service_type == 'wcs':
        result['wcs'] = WCSParser(xml_file)
    elif service_type == 'wfs':
        result['wfs'] = WFSParser(xml_file)
    
    return result


def fetch_capabilities(base_url: str, service_type: str, timeout: int = 30) -> Optional[bytes]:
    """
    Fetch GetCapabilities from a URL.
    
    Args:
        base_url: Base URL of the service
        service_type: Service type ('WMS', 'WCS', 'WFS')
        timeout: Request timeout in seconds
        
    Returns:
        XML content as bytes or None if failed
    """
    # Clean URL
    base_url = base_url.rstrip('?&')
    separator = '&' if '?' in base_url else '?'
    
    caps_url = f"{base_url}{separator}SERVICE={service_type}&REQUEST=GetCapabilities"
    
    try:
        req = Request(caps_url)
        req.add_header('User-Agent', 'ogc2qgis/0.1.0')
        
        with urlopen(req, timeout=timeout) as response:
            return response.read()
    except (URLError, HTTPError, TimeoutError):
        return None


def fetch_and_convert(
    base_url: str,
    output_dir: Optional[Union[str, Path]] = None,
    base_name: Optional[str] = None,
    qlr_mode: Optional[str] = None,
) -> Dict:
    """
    Fetch capabilities from URL and convert to QGIS configs.

    Args:
        base_url: Base URL of the OGC service
        output_dir: Directory to save output files (default: current directory)
        base_name: Prefix for output filenames (default: last URL path segment)

    Returns:
        Dict with service types as keys and output file paths as values (None if skipped)
    """
    import tempfile
    from pathlib import Path
    from urllib.parse import urlparse

    if output_dir is None:
        output_dir = Path.cwd()
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Resolve output filename prefix
    if base_name:
        url_base_name = base_name
    else:
        parsed_url = urlparse(base_url)
        path_parts = [p for p in parsed_url.path.split('/') if p]
        url_base_name = path_parts[-1] if path_parts else (parsed_url.hostname or 'output')

    results = {}

    for service_type in ['WMS', 'WCS', 'WFS']:
        content = fetch_capabilities(base_url, service_type)

        if content is None:
            results[service_type.lower()] = None
            continue

        # Save to temp file
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.xml', delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            # Parse and convert
            parsed = parse_capabilities(tmp_path)
            parser_key = service_type.lower()
            parser = parsed[parser_key]

            if parser is None:
                results[parser_key] = None
                continue

            # Skip if no meaningful data was found
            if parser_key == 'wms':
                has_data = bool(parser.server_url or parser.layers)
            elif parser_key == 'wcs':
                has_data = bool(parser.server_url or parser.coverages)
            else:  # wfs
                has_data = bool(parser.server_url or parser.features)

            if not has_data:
                results[parser_key] = None
                continue

            if qlr_mode != 'only':
                output_file = output_dir / f"{url_base_name}_{parser_key}2qgis.xml"
                parser.save(str(output_file))
                results[parser_key] = str(output_file)

            if qlr_mode in ('include', 'only'):
                qlr_file = output_dir / f"{url_base_name}_{parser_key}2qgis.qlr"
                parser.save_qlr(str(qlr_file))
                results[f'{parser_key}_qlr'] = str(qlr_file)
        finally:
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)

    return results
