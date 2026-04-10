"""Tests for compare functionality."""

import pytest
import tempfile
from pathlib import Path

from ogc2qgis.compare import compare_configs, normalize_url


def test_normalize_url():
    """Test URL normalization."""
    # Same URL different formats
    url1 = "https://server.com/geoserver/ows?SERVICE=WMS"
    url2 = "https://server.com/geoserver/ows/"
    url3 = "HTTPS://SERVER.COM/geoserver/ows"
    
    assert normalize_url(url1) == normalize_url(url2)
    assert normalize_url(url1) == normalize_url(url3)


def test_compare_identical_configs():
    """Test comparing identical WMS configs."""
    wms_config = '''<?xml version="1.0"?>
<!DOCTYPE connections>
<qgsWMSConnections version="1.0">
    <wms url="https://example.com/wms" name="Test Server" />
</qgsWMSConnections>'''
    
    # Create two identical temp files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f1:
        f1.write(wms_config)
        file1 = f1.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f2:
        f2.write(wms_config)
        file2 = f2.name
    
    try:
        result = compare_configs(file1, file2)
        
        assert result['identical'] == True
        assert result['same_service_type'] == True
        assert result['common_servers'] == 1
        assert len(result['only_in_file1']) == 0
        assert len(result['only_in_file2']) == 0
    finally:
        Path(file1).unlink(missing_ok=True)
        Path(file2).unlink(missing_ok=True)


def test_compare_different_configs():
    """Test comparing different WMS configs."""
    config1 = '''<?xml version="1.0"?>
<!DOCTYPE connections>
<qgsWMSConnections version="1.0">
    <wms url="https://server1.com/wms" name="Server 1" />
</qgsWMSConnections>'''
    
    config2 = '''<?xml version="1.0"?>
<!DOCTYPE connections>
<qgsWMSConnections version="1.0">
    <wms url="https://server2.com/wms" name="Server 2" />
</qgsWMSConnections>'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f1:
        f1.write(config1)
        file1 = f1.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f2:
        f2.write(config2)
        file2 = f2.name
    
    try:
        result = compare_configs(file1, file2)
        
        assert result['identical'] == False
        assert result['common_servers'] == 0
        assert len(result['only_in_file1']) == 1
        assert len(result['only_in_file2']) == 1
    finally:
        Path(file1).unlink(missing_ok=True)
        Path(file2).unlink(missing_ok=True)


def test_compare_partial_match():
    """Test comparing configs with some common servers."""
    config1 = '''<?xml version="1.0"?>
<!DOCTYPE connections>
<qgsWMSConnections version="1.0">
    <wms url="https://common.com/wms" name="Common" />
    <wms url="https://unique1.com/wms" name="Unique 1" />
</qgsWMSConnections>'''
    
    config2 = '''<?xml version="1.0"?>
<!DOCTYPE connections>
<qgsWMSConnections version="1.0">
    <wms url="https://common.com/wms" name="Common" />
    <wms url="https://unique2.com/wms" name="Unique 2" />
</qgsWMSConnections>'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f1:
        f1.write(config1)
        file1 = f1.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f2:
        f2.write(config2)
        file2 = f2.name
    
    try:
        result = compare_configs(file1, file2)
        
        assert result['identical'] == False
        assert result['common_servers'] == 1
        assert len(result['only_in_file1']) == 1
        assert len(result['only_in_file2']) == 1
        assert 'https://common.com/wms' in result['common_server_urls']
    finally:
        Path(file1).unlink(missing_ok=True)
        Path(file2).unlink(missing_ok=True)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
