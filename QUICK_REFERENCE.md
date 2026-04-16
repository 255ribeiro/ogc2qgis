# OGC2QGIS - Quick Reference Card

## 🐛 ACTIVE BUG
**WCS/WFS URL Extraction Failure**
- Files: `src/ogc2qgis/parsers/wcs.py`, `wfs.py`
- Issue: Empty URL in output configs
- Line: ~24-30 in each file
- Fix needed: Better XPath fallback patterns

## 📂 Key Files
```
src/ogc2qgis/
├── __init__.py          Public API
├── core.py              detect, parse, fetch functions
├── compare.py           compare_configs() ✨ NEW
├── parsers/
│   ├── wms.py          ✅ WORKS
│   ├── wcs.py          ❌ URL BROKEN
│   └── wfs.py          ❌ URL BROKEN
└── cli/main.py          convert, fetch, compare commands
```

## 🧪 Test Commands
```bash
# Test bug
ogc2qgis fetch https://geoservicos.inde.gov.br/geoserver/BAPSalvador/ows

# Expected: 3 files with valid URLs
# Actual: WCS/WFS have empty URLs

# Debug
curl "URL?SERVICE=WCS&REQUEST=GetCapabilities" > wcs.xml
grep -i "url\|href\|resource" wcs.xml
```

## 🔧 Fix Strategy
1. Download INDE WCS/WFS GetCapabilities
2. Find URL location in XML (compare with WMS)
3. Update XPath in parsers
4. Add fallback patterns like WMS has
5. Test

## 📦 Package Status
- Version: 0.1.0
- Language: Python 3.8+
- Dependencies: 0
- License: MIT
- Status: Pre-release (bug fix needed)

## 🎯 Commands
```bash
ogc2qgis convert file.xml
ogc2qgis fetch <url>
ogc2qgis compare file1.xml file2.xml  # ✨ NEW
```

## 💻 Library
```python
from ogc2qgis import parse_capabilities, compare_configs

configs = parse_capabilities('file.xml')
result = compare_configs('a.xml', 'b.xml')
```

## ✅ What Works
- WMS parsing ✅
- CLI commands ✅
- Compare function ✅
- Tests ✅
- Documentation ✅

## ❌ What's Broken
- WCS URL extraction
- WFS URL extraction

## 📝 Context
Full details in: PROJECT_CONTEXT.md
