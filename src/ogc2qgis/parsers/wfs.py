"""WFS GetCapabilities parser."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Union


class WFSParser:
    """Parser for WFS GetCapabilities documents."""
    
    def __init__(self, xml_file: Union[str, Path]):
        """
        Initialize WFS parser.
        
        Args:
            xml_file: Path to WFS GetCapabilities XML file
        """
        self.xml_file = Path(xml_file)
        self._tree = ET.parse(self.xml_file)
        self._root = self._tree.getroot()
        self._parse()
    
    def _parse(self):
        """Parse the WFS capabilities document."""
        ns = {
            'wfs': 'http://www.opengis.net/wfs',
            'ows': 'http://www.opengis.net/ows',
            'xlink': 'http://www.w3.org/1999/xlink'
        }
        
        # Extract server URL
        url_elem = self._root.find('.//ows:Operation[@name="GetFeature"]//ows:Get', ns)
        if url_elem is None:
            url_elem = self._root.find('.//Operation[@name="GetFeature"]//Get')
        
        self.server_url = ''
        if url_elem is not None:
            self.server_url = url_elem.get('{http://www.w3.org/1999/xlink}href', '')
        
        # Clean URL
        if '?' in self.server_url:
            self.server_url = self.server_url.split('?')[0]
        
        # Extract service title
        service_title = self._root.find('.//ows:ServiceIdentification/ows:Title', ns)
        if service_title is None:
            service_title = self._root.find('.//ServiceIdentification/Title')
        self.service_name = service_title.text if service_title is not None else "WFS Server"
        
        # Extract feature types
        self.features = []
        feature_elements = self._root.findall('.//wfs:FeatureType', ns)
        if not feature_elements:
            feature_elements = self._root.findall('.//FeatureType')
        
        for feature in feature_elements:
            # Try different formats
            name_elem = feature.find('wfs:Name', ns)
            if name_elem is None:
                name_elem = feature.find('Name')
            
            title_elem = feature.find('wfs:Title', ns)
            if title_elem is None:
                title_elem = feature.find('Title')
            
            if name_elem is not None and name_elem.text:
                feature_name = name_elem.text.strip()
                feature_title = title_elem.text.strip() if (title_elem is not None and title_elem.text) else feature_name
                
                self.features.append({
                    'name': feature_name,
                    'title': feature_title
                })
    
    def to_qgis_config(self) -> 'QGISWFSConfig':
        """
        Convert to QGIS WFS configuration.
        
        Returns:
            QGISWFSConfig object
        """
        return QGISWFSConfig(
            url=self.server_url,
            name=self.service_name,
            features=self.features
        )
    
    def save(self, output_file: Union[str, Path]):
        """
        Save as QGIS WFS configuration file.
        
        Args:
            output_file: Path to output XML file
        """
        config = self.to_qgis_config()
        config.save(output_file)


class QGISWFSConfig:
    """QGIS WFS connection configuration."""
    
    def __init__(self, url: str, name: str, features: List[Dict]):
        self.url = url
        self.name = name
        self.features = features
    
    def to_xml(self) -> ET.Element:
        """Generate XML element tree."""
        root = ET.Element('qgsWFSConnections', version='1.1')
        
        wfs = ET.SubElement(root, 'wfs')
        wfs.set('ignoreAxisOrientation', '0')
        wfs.set('version', 'auto')
        wfs.set('maxnumfeatures', '')
        wfs.set('pagesize', '')
        wfs.set('pagingenabled', '1')
        wfs.set('password', '')
        wfs.set('url', self.url)
        wfs.set('invertAxisOrientation', '0')
        wfs.set('username', '')
        wfs.set('name', self.name)
        
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
