"""Compare QGIS configuration files."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Union
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
