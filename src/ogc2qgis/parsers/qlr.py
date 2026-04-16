"""QGIS Layer Definition (.qlr) writers for WMS, WCS, and WFS services."""

import re
import uuid
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Union


def _make_layer_id() -> str:
    return uuid.uuid4().hex


def _detect_category(title: str) -> Optional[str]:
    """Extract category code from patterns like '3 - CBGE 1.1 Passeio'."""
    m = re.match(r'^\d+\s*[-\u2013]\s*([A-Z]{2,})', title)
    return m.group(1) if m else None


def _group_by_category(items: List[Dict]) -> Optional[Dict[str, List[Dict]]]:
    """
    Group items by category code detected from their 'title' field.
    Returns None when no categories are found (caller should use a flat layout).
    """
    groups: Dict[str, list] = defaultdict(list)
    categorised = 0

    for item in items:
        cat = _detect_category(item['title'])
        if cat:
            categorised += 1
            groups[cat].append(item)
        else:
            groups['Outros'].append(item)

    if categorised == 0:
        return None  # no pattern found — caller uses flat layout

    outros = groups.pop('Outros', [])
    result = dict(sorted(groups.items()))
    if outros:
        result['Outros'] = outros
    return result


class _BaseQLRWriter:
    """
    Base class for QGIS Layer Definition writers.

    Sub-classes must implement `_items()`, `_item_id()`, and `_datasource()`.
    They must also set `_provider` and `_layer_type` as class attributes.
    """

    _provider: str = ''
    _layer_type: str = 'vector'

    def __init__(self, url: str, service_name: str, group_name: Optional[str] = None):
        self.url = url
        self.service_name = service_name
        self.group_name = group_name or service_name

    # ── subclass interface ────────────────────────────────────────────────────

    def _items(self) -> List[Dict]:
        raise NotImplementedError

    def _item_id(self, item: Dict) -> str:
        """Return a stable unique key for the item (used as dict key, not layer ID)."""
        raise NotImplementedError

    def _datasource(self, item: Dict) -> str:
        raise NotImplementedError

    # ── tree building ─────────────────────────────────────────────────────────

    def _append_leaf(self, parent: ET.Element, item: Dict, layer_ids: Dict):
        leaf = ET.SubElement(parent, 'layer-tree-layer')
        leaf.set('id', layer_ids[self._item_id(item)])
        leaf.set('name', item['title'])
        leaf.set('checked', 'Qt::Checked')
        leaf.set('expanded', '1')
        leaf.set('source', self._datasource(item))
        leaf.set('providerKey', self._provider)
        ET.SubElement(leaf, 'custom-properties')

    def _build_tree(self, top: ET.Element, items: List[Dict], layer_ids: Dict):
        groups = _group_by_category(items)

        if groups is None:
            # Flat: all items directly under top group
            for item in items:
                self._append_leaf(top, item, layer_ids)
        else:
            for cat_name, cat_items in groups.items():
                cat_node = ET.SubElement(top, 'layer-tree-group')
                cat_node.set('name', cat_name)
                cat_node.set('checked', 'Qt::Checked')
                cat_node.set('expanded', '0')
                ET.SubElement(cat_node, 'custom-properties')
                for item in cat_items:
                    self._append_leaf(cat_node, item, layer_ids)

    # ── XML generation ────────────────────────────────────────────────────────

    def to_xml(self) -> str:
        """Build and return the full .qlr XML string."""
        items = self._items()
        layer_ids = {self._item_id(item): _make_layer_id() for item in items}

        root = ET.Element('qlr')

        # Layer tree
        tree = ET.SubElement(root, 'layer-tree-group')
        ET.SubElement(tree, 'custom-properties')

        top = ET.SubElement(tree, 'layer-tree-group')
        top.set('name', self.group_name)
        top.set('checked', 'Qt::Checked')
        top.set('expanded', '1')
        ET.SubElement(top, 'custom-properties')

        self._build_tree(top, items, layer_ids)

        # Map layers
        project_layers = ET.SubElement(root, 'projectlayers')
        for item in items:
            ml = ET.SubElement(project_layers, 'maplayer')
            ml.set('type', self._layer_type)
            ml.set('autoRefreshEnabled', '0')
            ml.set('autoRefreshTime', '0')

            ET.SubElement(ml, 'id').text = layer_ids[self._item_id(item)]
            ET.SubElement(ml, 'datasource').text = self._datasource(item)
            ET.SubElement(ml, 'layername').text = item['title']
            kw = ET.SubElement(ml, 'keywordList')
            ET.SubElement(kw, 'value')
            provider = ET.SubElement(ml, 'provider')
            provider.set('encoding', '')
            provider.text = self._provider
            ET.SubElement(ml, 'vectorjoins')
            ET.SubElement(ml, 'layerGeometryType').text = '4'

        ET.indent(root, space='    ')
        return '<!DOCTYPE qgis-layer-definition>\n' + ET.tostring(root, encoding='unicode')

    def save(self, output_file: Union[str, Path]):
        """Save to a .qlr file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(self.to_xml())


# ── Service-specific writers ──────────────────────────────────────────────────

class WFSQLRWriter(_BaseQLRWriter):
    """QLR writer for WFS feature types (vector layers)."""

    _provider = 'WFS'
    _layer_type = 'vector'

    def __init__(
        self,
        url: str,
        service_name: str,
        features: List[Dict],
        group_name: Optional[str] = None,
    ):
        super().__init__(url, service_name, group_name)
        self.features = features

    def _items(self) -> List[Dict]:
        return self.features

    def _item_id(self, item: Dict) -> str:
        return item['name']

    def _datasource(self, item: Dict) -> str:
        return f"url='{self.url}' typename='{item['name']}' version='auto'"


class WMSQLRWriter(_BaseQLRWriter):
    """QLR writer for WMS layers (raster)."""

    _provider = 'wms'
    _layer_type = 'raster'

    def __init__(
        self,
        url: str,
        service_name: str,
        layers: List[Dict],
        group_name: Optional[str] = None,
    ):
        super().__init__(url, service_name, group_name)
        self.layers = layers

    def _items(self) -> List[Dict]:
        return self.layers

    def _item_id(self, item: Dict) -> str:
        return item['name']

    def _datasource(self, item: Dict) -> str:
        return (
            f"contextualWMSLegend=0"
            f"&crs=EPSG:4674"
            f"&dpiMode=7"
            f"&featureCount=10"
            f"&format=image/png"
            f"&layers={item['name']}"
            f"&styles="
            f"&url={self.url}"
        )


class WCSQLRWriter(_BaseQLRWriter):
    """QLR writer for WCS coverages (raster)."""

    _provider = 'wcs'
    _layer_type = 'raster'

    def __init__(
        self,
        url: str,
        service_name: str,
        coverages: List[Dict],
        group_name: Optional[str] = None,
    ):
        super().__init__(url, service_name, group_name)
        self.coverages = coverages

    def _items(self) -> List[Dict]:
        return self.coverages

    def _item_id(self, item: Dict) -> str:
        return item['identifier']

    def _datasource(self, item: Dict) -> str:
        return (
            f"cache=AlwaysNetwork"
            f"&crs=EPSG:4674"
            f"&format="
            f"&identifier={item['identifier']}"
            f"&url={self.url}"
        )
