# OGC2QGIS Project - Complete Context Document

**Created:** 2025-04-10  
**Status:** Active Development  
**Next Environment:** Claude Code / VSCode

---

## 📋 Project Overview

### What This Is
A Python library and CLI tool that converts OGC Web Services GetCapabilities documents (WMS, WCS, WFS) into QGIS-compatible connection configuration XML files.

### Why It Exists
- **Problem:** QGIS users must manually configure each OGC server (URL, name, etc.)
- **Solution:** Automatically parse GetCapabilities XML and generate QGIS config files
- **Benefit:** Import hundreds of layers instantly instead of manual configuration

### Target Users
- GIS professionals using QGIS
- Organizations managing multiple OGC servers
- Teams sharing GIS configurations

---

## 🏗️ Project Structure

```
ogc2qgis/
├── pyproject.toml                 # Poetry configuration
├── README.md                      # Documentation
├── LICENSE                        # MIT License
├── src/ogc2qgis/
│   ├── __init__.py               # Public API
│   ├── core.py                   # Core functions (detect, parse, fetch)
│   ├── compare.py                # Configuration comparison ✨ NEW
│   ├── parsers/
│   │   ├── wms.py                # WMS GetCapabilities parser
│   │   ├── wcs.py                # WCS GetCapabilities parser
│   │   ├── wfs.py                # WFS GetCapabilities parser
│   │   └── __init__.py
│   └── cli/
│       ├── main.py               # CLI entry point
│       └── __init__.py
├── tests/
│   ├── test_basic.py             # Basic tests
│   └── test_compare.py           # Compare function tests ✨ NEW
├── examples/
│   ├── library_usage.py          # Library usage examples
│   ├── cli_usage.sh              # CLI usage examples
│   └── compare_configs_example.py # Compare usage ✨ NEW
└── .github/workflows/
    └── ci.yml                    # GitHub Actions CI/CD
```

---

## 🎯 Features Implemented

### ✅ Core Functionality
1. **Parse GetCapabilities**
   - Auto-detect service type (WMS/WCS/WFS)
   - Extract server URL, service name, layers
   - Handle multiple namespace formats

2. **Generate QGIS Configs**
   - Create `qgis_wms_connections.xml`
   - Create `qgis_wcs_connections.xml`
   - Create `qgis_wfs_connections.xml`
   - Proper XML structure with DOCTYPE

3. **Fetch from URLs**
   - Download GetCapabilities remotely
   - Process multiple service types
   - Save configs locally

4. **Compare Configurations** ✨ NEW
   - Compare two QGIS config files
   - Normalize URLs for accurate comparison
   - Identify common/unique servers
   - Available in both library and CLI

### ✅ CLI Commands
```bash
ogc2qgis convert <file.xml>              # Convert local file
ogc2qgis fetch <url>                     # Fetch from URL
ogc2qgis compare <file1.xml> <file2.xml> # Compare configs ✨ NEW
```

### ✅ Library API
```python
from ogc2qgis import (
    WMSParser, WCSParser, WFSParser,
    parse_capabilities,
    fetch_and_convert,
    compare_configs  # ✨ NEW
)
```

---

## 🐛 CURRENT BUGS - UNDER INVESTIGATION

### **Bug #1: WCS/WFS URL Extraction Failure**

**Severity:** Medium  
**Status:** Investigating  
**Discovered:** 2025-04-10

#### Symptoms
When running:
```bash
ogc2qgis fetch https://geoservicos.inde.gov.br/geoserver/BAPSalvador/ows
```

**Results:**
- ✅ `qgis_wms_connections.xml` - **WORKS** (URL extracted correctly)
- ❌ `qgis_wcs_connections.xml` - **FAILS** (empty URL: `url=""`)
- ❌ `qgis_wfs_connections.xml` - **FAILS** (empty URL: `url=""`)

#### Expected Output
```xml
<!-- WMS - WORKS -->
<wms url="https://geoservicos.inde.gov.br/geoserver/BAPSalvador/ows" name="GeoServer INDE"/>

<!-- WCS - BROKEN -->
<wcs url="" name="Web Coverage Service"/>  <!-- ❌ Empty URL -->

<!-- WFS - BROKEN -->
<wfs url="" name="WFS Server"/>  <!-- ❌ Empty URL -->
```

#### Root Cause Analysis

**WMS Parser (`wms.py`)** - WORKS ✅
```python
# Has robust fallback patterns
url_elem = self._root.find('.//wms:GetMap/wms:DCPType/wms:HTTP/wms:Get/wms:OnlineResource', ns)
if url_elem is None:
    url_elem = self._root.find('.//GetMap//Get/OnlineResource')  # ✅ Good fallback
```

**WCS Parser (`wcs.py`)** - FAILS ❌
```python
# Limited fallback
url_elem = self._root.find('.//ows:Operation[@name="GetCoverage"]//ows:Get', ns)
if url_elem is None:
    url_elem = self._root.find('.//Operation[@name="GetCoverage"]//Get')  # ⚠️ Not enough
```

**WFS Parser (`wfs.py`)** - FAILS ❌
```python
# Similar limited fallback
url_elem = self._root.find('.//ows:Operation[@name="GetFeature"]//ows:Get', ns)
# ⚠️ Missing comprehensive fallback patterns
```

#### Hypothesis
The INDE GeoServer uses:
1. Different XML namespaces than expected
2. Different tag structure for WCS/WFS
3. Different attribute names for the URL

The GetCapabilities XML **is being downloaded successfully** (files are created), but the **URL extraction XPath queries are failing**.

#### Investigation Steps Needed
1. **Download raw XML:**
   ```bash
   curl "https://geoservicos.inde.gov.br/geoserver/BAPSalvador/ows?SERVICE=WCS&REQUEST=GetCapabilities" > wcs_debug.xml
   curl "https://geoservicos.inde.gov.br/geoserver/BAPSalvador/ows?SERVICE=WFS&REQUEST=GetCapabilities" > wfs_debug.xml
   ```

2. **Inspect XML structure:**
   - Find how URL is stored in WCS GetCapabilities
   - Find how URL is stored in WFS GetCapabilities
   - Compare with WMS structure (which works)

3. **Test with other servers:**
   - Verify if issue is INDE-specific or general
   - Try with standard GeoServer demo servers

4. **Fix XPath patterns:**
   - Add more fallback patterns to WCS parser
   - Add more fallback patterns to WFS parser
   - Handle namespace variations better

#### Code Files Involved
- `src/ogc2qgis/parsers/wcs.py` - Line ~24-30 (URL extraction)
- `src/ogc2qgis/parsers/wfs.py` - Line ~24-30 (URL extraction)
- `src/ogc2qgis/core.py` - Line ~80-95 (fetch_capabilities function)

#### Test Case
```python
# Minimal test to reproduce
from ogc2qgis.parsers.wcs import WCSParser

parser = WCSParser('wcs_debug.xml')
print(f"URL found: '{parser.server_url}'")  # Currently prints: ''
# Should print: 'https://geoservicos.inde.gov.br/geoserver/BAPSalvador/ows'
```

---

## 📚 Development History (Conversation Summary)

### Phase 1: Initial Scripts
- Created standalone Python scripts for WMS/WCS/WFS conversion
- Worked with uploaded INDE Salvador GetCapabilities files
- Discussed QGIS XML format requirements
- Identified that QGIS needs **separate files** for each service type

### Phase 2: PyPI Package Development
- Decided to create professional PyPI package
- Chose **Poetry** as build tool
- **Zero dependencies** (stdlib only)
- Package name: `ogc2qgis`
- Python 3.8+ compatibility

### Phase 3: Package Structure
- Implemented `src/` layout (modern Python packaging)
- Created parsers for WMS, WCS, WFS
- Added CLI with `convert` and `fetch` commands
- Set up GitHub Actions for CI/CD
- Added comprehensive documentation

### Phase 4: Compare Function
- **User request:** Need to compare QGIS config files
- **Solution:** Added `compare_configs()` function
- **Features:**
  - Normalize URLs for comparison
  - Detect common/unique servers
  - CLI command: `ogc2qgis compare`
  - Library function available
  - Full test coverage

### Phase 5: Bug Discovery
- **User tested:** `ogc2qgis fetch` with INDE server
- **Discovered:** WCS/WFS parsers fail to extract URLs
- **Status:** Currently investigating
- **Next:** Need to fix URL extraction in WCS/WFS parsers

---

## 🎓 Technical Decisions Made

### Why Poetry?
- Modern dependency management
- Easy PyPI publishing
- Lock files for reproducibility
- Better than setuptools

### Why Zero Dependencies?
- Easier installation
- Fewer compatibility issues
- Lighter package
- More reliable

### Why src/ Layout?
- Modern Python packaging standard
- Avoids import issues during development
- Clearer separation

### Why Separate Parsers?
- Each OGC service has different XML structure
- Easier to maintain
- Better error handling per service type

---

## 🔧 Tools & Technologies

- **Language:** Python 3.8+
- **Build:** Poetry
- **Testing:** pytest
- **Linting:** black, ruff
- **CI/CD:** GitHub Actions
- **License:** MIT
- **Standard:** OGC Web Services (WMS 1.3.0, WCS 1.1.1, WFS 2.0)

---

## 📖 Key Files to Understand

### `pyproject.toml`
- Package metadata
- Dependencies (none!)
- CLI entry point configuration
- Tool configuration (black, ruff, pytest)

### `src/ogc2qgis/__init__.py`
- Public API exports
- What users can import
- Currently exports: parsers, core functions, compare_configs

### `src/ogc2qgis/core.py`
- `detect_service_type()` - Auto-detect WMS/WCS/WFS
- `parse_capabilities()` - Parse any GetCapabilities file
- `fetch_capabilities()` - Download from URL
- `fetch_and_convert()` - Download + convert + save

### `src/ogc2qgis/parsers/wms.py`
- Parse WMS GetCapabilities XML
- Extract: URL, service name, layers
- Generate QGIS WMS config
- **Status:** ✅ Working correctly

### `src/ogc2qgis/parsers/wcs.py`
- Parse WCS GetCapabilities XML
- Extract: URL, service name, coverages
- **Status:** ⚠️ URL extraction failing

### `src/ogc2qgis/parsers/wfs.py`
- Parse WFS GetCapabilities XML
- Extract: URL, service name, features
- **Status:** ⚠️ URL extraction failing

### `src/ogc2qgis/compare.py` ✨ NEW
- Compare two QGIS config files
- Normalize URLs for matching
- Return detailed comparison results
- **Status:** ✅ Working correctly

### `src/ogc2qgis/cli/main.py`
- CLI interface
- Commands: convert, fetch, compare
- Argument parsing
- **Status:** ✅ Working correctly

---

## 🧪 Test Coverage

### Existing Tests
```python
# tests/test_basic.py
- test_version()
- test_wms_parser_init()
- test_detect_service_type()
- test_qgis_config_generation()
- test_wms_config_save()

# tests/test_compare.py ✨ NEW
- test_normalize_url()
- test_compare_identical_configs()
- test_compare_different_configs()
- test_compare_partial_match()
```

### Tests Needed
- [ ] Test WCS parser with real INDE XML
- [ ] Test WFS parser with real INDE XML
- [ ] Test URL extraction fallback patterns
- [ ] Test with multiple GeoServer versions
- [ ] Integration test with fetch command

---

## 📝 Example Usage

### Convert Local File
```bash
ogc2qgis convert capabilities.xml
```

### Fetch from Remote Server
```bash
ogc2qgis fetch https://geoservicos.inde.gov.br/geoserver/BAPSalvador/ows
```

### Compare Configurations
```bash
ogc2qgis compare old.xml new.xml
```

### As Python Library
```python
from ogc2qgis import parse_capabilities, compare_configs

# Parse
configs = parse_capabilities('ows.xml')
if configs['wms']:
    configs['wms'].save('qgis_wms_connections.xml')

# Compare
result = compare_configs('file1.xml', 'file2.xml')
if result['identical']:
    print("Same server!")
```

---

## 🚀 Next Steps

### Immediate Priority
1. **Fix WCS/WFS URL extraction bug**
   - Download INDE WCS/WFS GetCapabilities
   - Analyze XML structure
   - Update XPath patterns
   - Add better fallbacks
   - Test with multiple servers

2. **Add comprehensive tests**
   - Test with real OGC servers
   - Test edge cases
   - Test different GeoServer versions

### Future Enhancements
- [ ] Support WMS-T (temporal)
- [ ] Validate XML schemas
- [ ] Merge multiple configs
- [ ] GUI tool (Tkinter/Qt)
- [ ] QGIS plugin version
- [ ] Support for other OGC standards (WMTS, SOS)

### Publication
- [ ] Complete testing
- [ ] Final documentation review
- [ ] Publish to PyPI
- [ ] Create GitHub repository
- [ ] Setup GitHub Actions auto-publish

---

## 🌐 Test Servers

### Working
- INDE Brazil Salvador: `https://geoservicos.inde.gov.br/geoserver/BAPSalvador/ows`
  - WMS: ✅ Works
  - WCS: ❌ URL extraction fails
  - WFS: ❌ URL extraction fails

### To Test
- GeoServer demo server
- MapServer instances
- QGIS Server
- Other INDE regions

---

## 💡 Design Patterns Used

### Parser Pattern
Each service type (WMS/WCS/WFS) has its own parser class:
- Consistent interface
- Service-specific logic
- Easy to extend

### Factory Pattern
`parse_capabilities()` auto-detects type and returns appropriate parser

### Builder Pattern
`QGISWMSConfig`, `QGISWCSConfig`, `QGISWFSConfig` build XML incrementally

---

## 🔍 Debugging Tips

### Enable Verbose Output
```bash
ogc2qgis fetch <url> -v
```

### Test Parsers Directly
```python
from ogc2qgis.parsers.wcs import WCSParser

parser = WCSParser('debug.xml')
print(f"URL: {parser.server_url}")
print(f"Service: {parser.service_name}")
print(f"Coverages: {len(parser.coverages)}")
```

### Check Raw XML
```bash
curl "URL?SERVICE=WCS&REQUEST=GetCapabilities" | xmllint --format -
```

### Compare Working vs Broken
```bash
# WMS (works)
curl "URL?SERVICE=WMS&REQUEST=GetCapabilities" > wms.xml

# WCS (broken)
curl "URL?SERVICE=WCS&REQUEST=GetCapabilities" > wcs.xml

# Compare structures
diff wms.xml wcs.xml
```

---

## 📞 Original Requirements

From the conversation, the user wanted:
1. ✅ Convert OGC GetCapabilities to QGIS configs
2. ✅ Separate files for WMS/WCS/WFS
3. ✅ CLI tool for easy use
4. ✅ Python library for automation
5. ✅ Compare QGIS configs
6. ✅ Publish to PyPI
7. ⚠️ Handle various OGC server implementations (IN PROGRESS)

---

## 🎯 Success Criteria

- [ ] WCS parser extracts URLs correctly
- [ ] WFS parser extracts URLs correctly
- [ ] Works with major OGC server implementations
- [ ] Published on PyPI
- [ ] Documentation complete
- [ ] 90%+ test coverage
- [ ] CI/CD passing

---

## 📚 Reference Documentation

### OGC Standards
- WMS 1.3.0: https://www.ogc.org/standards/wms
- WCS 1.1.1: https://www.ogc.org/standards/wcs
- WFS 2.0: https://www.ogc.org/standards/wfs

### QGIS
- QGIS Documentation: https://docs.qgis.org/
- QGIS Server: https://docs.qgis.org/3.28/en/docs/server_manual/

### Python Packaging
- Poetry: https://python-poetry.org/
- PyPI: https://pypi.org/

---

## 🤝 Collaboration Notes

### For Claude Code / VSCode
When you open this project:

1. **Read this file first** for full context
2. **Focus on:** `src/ogc2qgis/parsers/wcs.py` and `wfs.py`
3. **Current task:** Fix URL extraction in WCS/WFS parsers
4. **Test with:** INDE Salvador server

### Questions to Ask Claude Code
- "Analyze the WCS GetCapabilities XML structure from INDE server"
- "Compare WMS vs WCS URL extraction patterns"
- "Suggest XPath patterns for robust URL extraction"
- "Add fallback patterns to WCS/WFS parsers"

---

## 📋 Checklist for Next Session

- [ ] Download WCS GetCapabilities from INDE
- [ ] Download WFS GetCapabilities from INDE
- [ ] Analyze XML structure
- [ ] Identify URL location in XML
- [ ] Update WCS parser XPath patterns
- [ ] Update WFS parser XPath patterns
- [ ] Test with INDE server
- [ ] Test with other servers
- [ ] Run test suite
- [ ] Document fix

---

**END OF CONTEXT DOCUMENT**

Last updated: 2025-04-10  
Ready for: Claude Code / VSCode  
Status: Active development, bug investigation phase
