"""OGC Capabilities parsers for WMS, WCS, and WFS."""

from ogc2qgis.parsers.wms import WMSParser
from ogc2qgis.parsers.wcs import WCSParser
from ogc2qgis.parsers.wfs import WFSParser

__all__ = ["WMSParser", "WCSParser", "WFSParser"]
