"""WCS GetCapabilities parser."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Union


class WCSParser:
    """Parser for WCS GetCapabilities documents."""
    
    def __init__(self, xml_file: Union[str, Path]):
        """
        Initialize WCS parser.
        
        Args:
            xml_file: Path to WCS GetCapabilities XML file
        """
        self.xml_file = Path(xml_file)
        self._tree = ET.parse(self.xml_file)
        self._root = self._tree.getroot()
        self._parse()
    
    def _parse(self):
        """Parse the WCS capabilities document."""
        ns = {
            'wcs': 'http://www.opengis.net/wcs/1.1.1',
            'ows': 'http://www.opengis.net/ows/1.1',
            'xlink': 'http://www.w3.org/1999/xlink'
        }
        
        # Extract server URL
        url_elem = self._root.find('.//ows:Operation[@name="GetCoverage"]//ows:Get', ns)
        if url_elem is None:
            url_elem = self._root.find('.//Operation[@name="GetCoverage"]//Get')
        
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
        self.service_name = service_title.text if service_title is not None else "WCS Server"
        
        # Extract coverages
        self.coverages = []
        
        # Try with full namespace first
        coverage_elements = self._root.findall('.//{http://www.opengis.net/wcs/1.1.1}CoverageSummary')
        
        # Fallback patterns
        if not coverage_elements:
            coverage_elements = self._root.findall('.//wcs:CoverageSummary', ns)
        if not coverage_elements:
            coverage_elements = self._root.findall('.//CoverageSummary')
        
        for coverage in coverage_elements:
            # Try different formats
            identifier_elem = coverage.find('{http://www.opengis.net/wcs/1.1.1}Identifier')
            if identifier_elem is None:
                identifier_elem = coverage.find('wcs:Identifier', ns)
            if identifier_elem is None:
                identifier_elem = coverage.find('Identifier')
            
            title_elem = coverage.find('{http://www.opengis.net/ows/1.1}Title')
            if title_elem is None:
                title_elem = coverage.find('ows:Title', ns)
            if title_elem is None:
                title_elem = coverage.find('Title')
            
            if identifier_elem is not None and identifier_elem.text:
                coverage_id = identifier_elem.text.strip()
                coverage_title = title_elem.text.strip() if (title_elem is not None and title_elem.text) else coverage_id
                
                self.coverages.append({
                    'identifier': coverage_id,
                    'title': coverage_title
                })
    
    def to_qgis_config(self) -> 'QGISWCSConfig':
        """
        Convert to QGIS WCS configuration.
        
        Returns:
            QGISWCSConfig object
        """
        return QGISWCSConfig(
            url=self.server_url,
            name=self.service_name,
            coverages=self.coverages
        )
    
    def save(self, output_file: Union[str, Path]):
        """
        Save as QGIS WCS configuration file.
        
        Args:
            output_file: Path to output XML file
        """
        config = self.to_qgis_config()
        config.save(output_file)


class QGISWCSConfig:
    """QGIS WCS connection configuration."""
    
    def __init__(self, url: str, name: str, coverages: List[Dict]):
        self.url = url
        self.name = name
        self.coverages = coverages
    
    def to_xml(self) -> ET.Element:
        """Generate XML element tree."""
        root = ET.Element('qgsWCSConnections', version='1.0')
        
        wcs = ET.SubElement(root, 'wcs')
        wcs.set('ignoreAxisOrientation', '0')
        wcs.set('invertAxisOrientation', '0')
        wcs.set('password', '')
        wcs.set('url', self.url)
        wcs.set('username', '')
        wcs.set('name', self.name)
        
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
