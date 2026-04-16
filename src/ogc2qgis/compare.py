"""Compare QGIS configuration files and live OGC web services."""

import socket
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Union
from urllib.parse import urlparse


def normalize_url(url: str) -> str:
    """
    Normalize URL for comparison.
    
    Args:
        url: URL to normalize
        
    Returns:
        Normalized URL string
    """
    if not url:
        return ""
    
    parsed = urlparse(url)
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    normalized = normalized.rstrip('/?&')
    
    return normalized.lower()


def parse_qgis_config(xml_file: Union[str, Path]) -> Dict:
    """
    Parse QGIS config file and extract connection information.
    
    Args:
        xml_file: Path to QGIS configuration XML file
        
    Returns:
        Dictionary with 'type' and 'connections' information
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Detect service type
    if 'WMS' in root.tag:
        service_type = 'wms'
        connection_tag = 'wms'
    elif 'WCS' in root.tag:
        service_type = 'wcs'
        connection_tag = 'wcs'
    elif 'WFS' in root.tag:
        service_type = 'wfs'
        connection_tag = 'wfs'
    else:
        return {'type': 'unknown', 'connections': []}
    
    connections = []
    for conn in root.findall(connection_tag):
        url = conn.get('url', '')
        name = conn.get('name', '')
        
        connections.append({
            'name': name,
            'url': url,
            'normalized_url': normalize_url(url)
        })
    
    return {
        'type': service_type,
        'connections': connections
    }


def compare_configs(file1: Union[str, Path], file2: Union[str, Path]) -> Dict:
    """
    Compare two QGIS config files.
    
    Args:
        file1: Path to first QGIS configuration file
        file2: Path to second QGIS configuration file
        
    Returns:
        Dictionary containing comparison results with keys:
        - same_service_type: bool
        - service_type1/2: str
        - total_connections_file1/2: int
        - common_servers: int
        - common_server_urls: list
        - only_in_file1/2: list
        - identical: bool
    """
    config1 = parse_qgis_config(file1)
    config2 = parse_qgis_config(file2)
    
    same_type = config1['type'] == config2['type']
    
    urls1 = {conn['normalized_url'] for conn in config1['connections']}
    urls2 = {conn['normalized_url'] for conn in config2['connections']}
    
    common_urls = urls1 & urls2
    only_in_file1 = urls1 - urls2
    only_in_file2 = urls2 - urls1
    
    common_connections = []
    for url in common_urls:
        conn1 = next((c for c in config1['connections'] if c['normalized_url'] == url), None)
        conn2 = next((c for c in config2['connections'] if c['normalized_url'] == url), None)
        
        if conn1 and conn2:
            common_connections.append({
                'url': url,
                'file1_name': conn1['name'],
                'file2_name': conn2['name'],
                'same_name': conn1['name'] == conn2['name']
            })
    
    return {
        'file1': str(file1),
        'file2': str(file2),
        'same_service_type': same_type,
        'service_type1': config1['type'],
        'service_type2': config2['type'],
        'total_connections_file1': len(config1['connections']),
        'total_connections_file2': len(config2['connections']),
        'common_servers': len(common_urls),
        'common_server_urls': sorted(common_urls),
        'common_connections': common_connections,
        'only_in_file1': sorted(only_in_file1),
        'only_in_file2': sorted(only_in_file2),
        'identical': (
            same_type and
            len(common_urls) > 0 and
            len(only_in_file1) == 0 and
            len(only_in_file2) == 0
        )
    }


def _fetch_and_parse(url: str, service_type: Optional[str] = None) -> Dict:
    """
    Fetch a GetCapabilities document and return parsed data.

    Returns a dict with keys: service_type, server_url, service_name, layers
    (layers is a generic term covering WMS layers / WCS coverages / WFS features).
    Returns None values on fetch/parse failure.
    """
    from ogc2qgis.core import fetch_capabilities, detect_service_type
    from ogc2qgis.parsers.wms import WMSParser
    from ogc2qgis.parsers.wcs import WCSParser
    from ogc2qgis.parsers.wfs import WFSParser

    types_to_try = [service_type.upper()] if service_type else ['WMS', 'WCS', 'WFS']

    for stype in types_to_try:
        content = fetch_capabilities(url, stype)
        if content is None:
            continue

        with tempfile.NamedTemporaryFile(mode='wb', suffix='.xml', delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            detected = detect_service_type(tmp_path)
            if detected is None:
                continue

            if detected == 'wms':
                parser = WMSParser(tmp_path)
                layers = [l['name'] for l in parser.layers]
            elif detected == 'wcs':
                parser = WCSParser(tmp_path)
                layers = [c['identifier'] for c in parser.coverages]
            else:
                parser = WFSParser(tmp_path)
                layers = [f['name'] for f in parser.features]

            return {
                'url': url,
                'service_type': detected,
                'server_url': normalize_url(parser.server_url),
                'service_name': parser.service_name,
                'layers': layers,
                'error': None,
            }
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    return {
        'url': url,
        'service_type': None,
        'server_url': None,
        'service_name': None,
        'layers': [],
        'error': f"Could not fetch or parse GetCapabilities from {url}",
    }


def compare_web(url1: str, url2: str, service_type: Optional[str] = None) -> Dict:
    """
    Compare two live OGC service URLs to determine if they point to the same server.

    Fetches GetCapabilities from both URLs and compares:
    - The server URL reported inside the document
    - The service name
    - The set of published layers / coverages / features

    Args:
        url1: First OGC service base URL
        url2: Second OGC service base URL
        service_type: Force a specific type ('wms', 'wcs', 'wfs').
                      If None, auto-detects from GetCapabilities.

    Returns:
        Dict with comparison results including a 'verdict' key:
        'identical'  – same reported URL, name, and layers
        'same_server' – same reported URL but different name or layers
        'different'  – different servers
        'error'      – one or both URLs could not be fetched
    """
    info1 = _fetch_and_parse(url1, service_type)
    info2 = _fetch_and_parse(url2, service_type)

    if info1['error'] or info2['error']:
        return {
            'url1': url1,
            'url2': url2,
            'info1': info1,
            'info2': info2,
            'same_service_type': False,
            'same_server_url': False,
            'same_service_name': False,
            'common_layers': [],
            'only_in_url1': [],
            'only_in_url2': [],
            'layer_overlap_pct': 0.0,
            'verdict': 'error',
        }

    same_type = info1['service_type'] == info2['service_type']
    same_server_url = bool(
        info1['server_url']
        and info2['server_url']
        and info1['server_url'] == info2['server_url']
    )
    same_name = info1['service_name'] == info2['service_name']

    set1 = set(info1['layers'])
    set2 = set(info2['layers'])
    common = sorted(set1 & set2)
    only1 = sorted(set1 - set2)
    only2 = sorted(set2 - set1)
    total = len(set1 | set2)
    overlap_pct = (len(common) / total * 100) if total else 0.0

    if same_server_url and same_name and not only1 and not only2:
        verdict = 'identical'
    elif same_server_url:
        verdict = 'same_server'
    else:
        verdict = 'different'

    return {
        'url1': url1,
        'url2': url2,
        'info1': info1,
        'info2': info2,
        'same_service_type': same_type,
        'same_server_url': same_server_url,
        'same_service_name': same_name,
        'common_layers': common,
        'only_in_url1': only1,
        'only_in_url2': only2,
        'layer_overlap_pct': round(overlap_pct, 1),
        'verdict': verdict,
    }


def _resolve_ips(hostname: str) -> Dict:
    """Resolve all IPs for a hostname. Returns dict with 'ips' and 'error'."""
    try:
        results = socket.getaddrinfo(hostname, None)
        ips = sorted({r[4][0] for r in results})
        return {'hostname': hostname, 'ips': ips, 'error': None}
    except socket.gaierror as e:
        return {'hostname': hostname, 'ips': [], 'error': str(e)}


def compare_ip(url1: str, url2: str) -> Dict:
    """
    Compare two URLs by resolving their hostnames to IP addresses.

    Args:
        url1: First URL
        url2: Second URL

    Returns:
        Dict with keys:
        - host1 / host2: hostnames extracted from the URLs
        - ips1 / ips2: sorted lists of resolved IP addresses
        - common_ips: IPs present in both
        - same_host: True if hostnames are identical
        - same_ip: True if at least one IP is shared
        - identical: True if both hostname and all IPs match exactly
        - error1 / error2: resolution error messages (None if ok)
    """
    host1 = urlparse(url1).hostname or ''
    host2 = urlparse(url2).hostname or ''

    res1 = _resolve_ips(host1)
    res2 = _resolve_ips(host2)

    set1 = set(res1['ips'])
    set2 = set(res2['ips'])
    common = sorted(set1 & set2)

    return {
        'url1': url1,
        'url2': url2,
        'host1': host1,
        'host2': host2,
        'ips1': res1['ips'],
        'ips2': res2['ips'],
        'common_ips': common,
        'same_host': host1.lower() == host2.lower(),
        'same_ip': bool(common),
        'identical': host1.lower() == host2.lower() and set1 == set2,
        'error1': res1['error'],
        'error2': res2['error'],
    }
