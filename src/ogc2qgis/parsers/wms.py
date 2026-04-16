"""WMS GetCapabilities parser."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Union


class WMSParser:
    """Parser for WMS GetCapabilities documents."""
    
    def __init__(self, xml_file: Union[str, Path]):
        """
        Initialize WMS parser.
        
        Args:
            xml_file: Path to WMS GetCapabilities XML file
        """
        self.xml_file = Path(xml_file)
        self._tree = ET.parse(self.xml_file)
        self._root = self._tree.getroot()
        self._parse()
    
    def _parse(self):
        """Parse the WMS capabilities document."""
        ns = {
            'wms': 'http://www.opengis.net/wms',
            'xlink': 'http://www.w3.org/1999/xlink'
        }
        
        # Extract server URL
        url_elem = self._root.find('.//wms:GetMap/wms:DCPType/wms:HTTP/wms:Get/wms:OnlineResource', ns)
        if url_elem is None:
            url_elem = self._root.find('.//GetMap//Get/OnlineResource')
        
        self.server_url = ''
        if url_elem is not None:
            self.server_url = url_elem.get('{http://www.w3.org/1999/xlink}href', '')
        
        # Clean URL
        if '?' in self.server_url:
            self.server_url = self.server_url.split('?')[0]
        
        # Extract service title
        service_title = self._root.find('.//wms:Service/wms:Title', ns)
        if service_title is None:
            service_title = self._root.find('.//Service/Title')
        self.service_name = service_title.text if service_title is not None else "WMS Server"
        
        # Extract layers
        self.layers = []
        layer_elements = self._root.findall('.//wms:Layer/wms:Layer', ns)
        if not layer_elements:
            layer_elements = self._root.findall('.//Layer/Layer')
        
        for layer in layer_elements:
            # Try different name tag formats
            name_elem = layer.find('wms:Name', ns)
            if name_elem is None:
                name_elem = layer.find('Name')
            if name_elem is None:
                name_elem = layer.find('n')  # GeoServer format
            
            title_elem = layer.find('wms:Title', ns)
            if title_elem is None:
                title_elem = layer.find('Title')
            
            if name_elem is not None and name_elem.text:
                layer_name = name_elem.text.strip()
                layer_title = title_elem.text.strip() if (title_elem is not None and title_elem.text) else layer_name
                
                self.layers.append({
                    'name': layer_name,
                    'title': layer_title
                })
    
    def to_qgis_config(self) -> 'QGISWMSConfig':
        """
        Convert to QGIS WMS configuration.
        
        Returns:
            QGISWMSConfig object
        """
        return QGISWMSConfig(
            url=self.server_url,
            name=self.service_name,
            layers=self.layers
        )
    
    def save(self, output_file: Union[str, Path]):
        """Save as QGIS WMS configuration file."""
        config = self.to_qgis_config()
        config.save(output_file)

    def save_qlr(self, output_file: Union[str, Path], group_name: Optional[str] = None):
        """Save as a QGIS Layer Definition (.qlr) with layers grouped by category."""
        from ogc2qgis.parsers.qlr import WMSQLRWriter
        WMSQLRWriter(
            url=self.server_url,
            service_name=self.service_name,
            layers=self.layers,
            group_name=group_name,
        ).save(output_file)


class QGISWMSConfig:
    """QGIS WMS connection configuration."""
    
    def __init__(self, url: str, name: str, layers: List[Dict]):
        self.url = url
        self.name = name
        self.layers = layers
    
    def to_xml(self) -> ET.Element:
        """Generate XML element tree."""
        root = ET.Element('qgsWMSConnections', version='1.0')
        
        wms = ET.SubElement(root, 'wms')
        wms.set('ignoreGetFeatureInfoURI', '0')
        wms.set('ignoreGetMapURI', '0')
        wms.set('ignoreReportedLayerExtents', '0')
        wms.set('invertAxisOrientation', '0')
        wms.set('smoothPixmapTransform', '0')
        wms.set('dpiMode', '7')
        wms.set('password', '')
        wms.set('url', self.url)
        wms.set('username', '')
        wms.set('name', self.name)
        
        ET.indent(root, space='    ')
        return root
    
    def save(self, output_file: Union[str, Path]):
        """Save to XML file."""
        root = self.to_xml()
        
        # Create DOCTYPE manually
        xml_string = '<!DOCTYPE connections>\n'
        xml_string += ET.tostring(root, encoding='unicode')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_string)
