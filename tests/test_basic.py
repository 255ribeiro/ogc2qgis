"""Basic tests for ogc2qgis package."""

import pytest
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET

from ogc2qgis import WMSParser, WCSParser, WFSParser
from ogc2qgis.core import detect_service_type


def test_version():
    """Test that package has version."""
    import ogc2qgis
    assert hasattr(ogc2qgis, '__version__')
    assert isinstance(ogc2qgis.__version__, str)


def test_wms_parser_init():
    """Test WMS parser can be instantiated."""
    # Create minimal WMS XML
    xml_content = '''<?xml version="1.0"?>
    <WMS_Capabilities version="1.3.0">
        <Service>
            <Title>Test WMS</Title>
        </Service>
        <Capability>
            <Request>
                <GetMap>
                    <DCPType>
                        <HTTP>
                            <Get>
                                <OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" 
                                    xlink:href="http://example.com/wms"/>
                            </Get>
                        </HTTP>
                    </DCPType>
                </GetMap>
            </Request>
        </Capability>
    </WMS_Capabilities>'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write(xml_content)
        temp_path = f.name
    
    try:
        parser = WMSParser(temp_path)
        assert parser.service_name == "Test WMS"
        assert parser.server_url == "http://example.com/wms"
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_detect_service_type():
    """Test service type detection."""
    # WMS XML
    wms_xml = '''<?xml version="1.0"?>
    <WMS_Capabilities version="1.3.0">
        <Service><Title>Test</Title></Service>
    </WMS_Capabilities>'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write(wms_xml)
        temp_path = f.name
    
    try:
        service_type = detect_service_type(temp_path)
        assert service_type == 'wms'
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_qgis_config_generation():
    """Test QGIS config XML generation."""
    from ogc2qgis.parsers.wms import QGISWMSConfig
    
    config = QGISWMSConfig(
        url="http://example.com/wms",
        name="Test Server",
        layers=[]
    )
    
    root = config.to_xml()
    assert root.tag == 'qgsWMSConnections'
    assert root.get('version') == '1.0'
    
    wms = root.find('wms')
    assert wms is not None
    assert wms.get('url') == "http://example.com/wms"
    assert wms.get('name') == "Test Server"


def test_wms_config_save():
    """Test saving WMS config to file."""
    from ogc2qgis.parsers.wms import QGISWMSConfig
    
    config = QGISWMSConfig(
        url="http://example.com/wms",
        name="Test Server",
        layers=[]
    )
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        temp_path = f.name
    
    try:
        config.save(temp_path)
        
        # Verify file exists and is valid XML
        assert Path(temp_path).exists()
        
        tree = ET.parse(temp_path)
        root = tree.getroot()
        assert root.tag == 'qgsWMSConnections'
    finally:
        Path(temp_path).unlink(missing_ok=True)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
