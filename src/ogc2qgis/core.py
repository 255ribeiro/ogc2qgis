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


def fetch_and_convert(base_url: str, output_dir: Optional[Union[str, Path]] = None) -> Dict:
    """
    Fetch capabilities from URL and convert to QGIS configs.
    
    Args:
        base_url: Base URL of the OGC service
        output_dir: Directory to save output files (default: current directory)
        
    Returns:
        Dict with service types as keys and config objects as values
    """
    import tempfile
    from pathlib import Path
    
    if output_dir is None:
        output_dir = Path.cwd()
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
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
            
            if parsed[parser_key]:
                # Generate QGIS config
                output_file = output_dir / f"qgis_{parser_key}_connections.xml"
                parsed[parser_key].save(str(output_file))
                results[parser_key] = str(output_file)
            else:
                results[parser_key] = None
        finally:
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)
    
    return results
