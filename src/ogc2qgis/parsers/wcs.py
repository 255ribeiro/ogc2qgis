"""WCS GetCapabilities parser."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Union


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
    
    # Known OWS namespace variants used across WCS versions
    _OWS_NS = [
        'http://www.opengis.net/ows/1.1',   # WCS 1.1.x
        'http://www.opengis.net/ows/2.0',   # WCS 2.0.x
        'http://www.opengis.net/ows',        # older/generic
    ]
    _WCS_NS = [
        'http://www.opengis.net/wcs/1.1.1',
        'http://www.opengis.net/wcs/1.1',
        'http://www.opengis.net/wcs/2.0',
    ]

    def _find_url_elem(self):
        """Return the Get element for GetCoverage across namespace variants."""
        xlink = 'http://www.w3.org/1999/xlink'
        for ows in self._OWS_NS:
            ns = {'ows': ows, 'xlink': xlink}
            elem = self._root.find('.//ows:Operation[@name="GetCoverage"]//ows:Get', ns)
            if elem is not None:
                return elem
        # Namespace-wildcard fallback (Python 3.8+)
        return self._root.find('.//{*}Operation[@name="GetCoverage"]//{*}Get')

    def _parse(self):
        """Parse the WCS capabilities document."""
        xlink = 'http://www.w3.org/1999/xlink'

        # Extract server URL
        url_elem = self._find_url_elem()
        self.server_url = ''
        if url_elem is not None:
            self.server_url = url_elem.get(f'{{{xlink}}}href', '')
        if '?' in self.server_url:
            self.server_url = self.server_url.split('?')[0]

        # Extract service title — try all ows namespace variants
        service_title = None
        for ows in self._OWS_NS:
            ns = {'ows': ows}
            service_title = self._root.find('.//ows:ServiceIdentification/ows:Title', ns)
            if service_title is not None:
                break
        if service_title is None:
            service_title = self._root.find('.//{*}ServiceIdentification/{*}Title')
        self.service_name = service_title.text if service_title is not None else "WCS Server"

        # Extract coverages — try all wcs namespace variants
        self.coverages = []
        coverage_elements = []
        for wcs in self._WCS_NS:
            coverage_elements = self._root.findall(f'.//{{{wcs}}}CoverageSummary')
            if coverage_elements:
                break
        if not coverage_elements:
            coverage_elements = self._root.findall('.//{*}CoverageSummary')

        for coverage in coverage_elements:
            # WCS 2.0 uses CoverageId; WCS 1.1.x uses Identifier
            identifier_elem = None
            for wcs in self._WCS_NS:
                identifier_elem = coverage.find(f'{{{wcs}}}CoverageId')
                if identifier_elem is not None:
                    break
                identifier_elem = coverage.find(f'{{{wcs}}}Identifier')
                if identifier_elem is not None:
                    break
            if identifier_elem is None:
                identifier_elem = coverage.find('{*}CoverageId')
            if identifier_elem is None:
                identifier_elem = coverage.find('{*}Identifier')

            title_elem = None
            for ows in self._OWS_NS:
                title_elem = coverage.find(f'{{{ows}}}Title')
                if title_elem is not None:
                    break
            if title_elem is None:
                title_elem = coverage.find('{*}Title')

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
        """Save as QGIS WCS configuration file."""
        config = self.to_qgis_config()
        config.save(output_file)

    def save_qlr(self, output_file: Union[str, Path], group_name: Optional[str] = None):
        """Save as a QGIS Layer Definition (.qlr) with coverages grouped by category."""
        from ogc2qgis.parsers.qlr import WCSQLRWriter
        WCSQLRWriter(
            url=self.server_url,
            service_name=self.service_name,
            coverages=self.coverages,
            group_name=group_name,
        ).save(output_file)


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
