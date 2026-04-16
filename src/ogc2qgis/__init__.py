"""
ogc2qgis - Convert OGC Web Services to QGIS configurations.

A Python library and CLI tool to convert OGC GetCapabilities documents (WMS, WCS, WFS)
into QGIS-compatible connection configuration files.
"""

__version__ = "0.1.3"
__author__ = "OGC2QGIS Contributors"
__license__ = "MIT"

from ogc2qgis.parsers.wms import WMSParser
from ogc2qgis.parsers.wcs import WCSParser
from ogc2qgis.parsers.wfs import WFSParser
from ogc2qgis.parsers.qlr import WFSQLRWriter, WMSQLRWriter, WCSQLRWriter
from ogc2qgis.core import (
    parse_capabilities,
    detect_service_type,
    fetch_and_convert,
)
from ogc2qgis.compare import compare_configs, compare_web, compare_ip

__all__ = [
    "WMSParser",
    "WCSParser",
    "WFSParser",
    "WFSQLRWriter",
    "WMSQLRWriter",
    "WCSQLRWriter",
    "parse_capabilities",
    "detect_service_type",
    "fetch_and_convert",
    "compare_configs",
    "compare_web",
    "compare_ip",
]
