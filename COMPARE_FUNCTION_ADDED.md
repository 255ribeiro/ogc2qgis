# ✅ compare_configs Added to ogc2qgis Library

## Changes Made

### 1. New Module Added
**File**: `src/ogc2qgis/compare.py`
- `compare_configs(file1, file2)` - Compare two QGIS config files
- `parse_qgis_config(xml_file)` - Parse QGIS config XML
- `normalize_url(url)` - Normalize URLs for comparison

### 2. Updated Main Package
**File**: `src/ogc2qgis/__init__.py`
- Added `compare_configs` to exports
- Now available: `from ogc2qgis import compare_configs`

### 3. Tests Added
**File**: `tests/test_compare.py`
- Test URL normalization
- Test identical configs
- Test different configs  
- Test partial matches

### 4. Example Added
**File**: `examples/compare_configs_example.py`
- Shows 4 usage examples
- Deployment validation
- Connection name checking

---

## Usage

### Basic Usage
```python
from ogc2qgis import compare_configs

result = compare_configs('file1.xml', 'file2.xml')

if result['identical']:
    print("✅ Same server and capabilities")
elif result['common_servers'] > 0:
    print(f"⚠️ {result['common_servers']} common servers")
else:
    print("❌ Completely different")
```

### Check Details
```python
# Check common servers
print(result['common_server_urls'])

# Check differences
print(result['only_in_file1'])  # Unique to file 1
print(result['only_in_file2'])  # Unique to file 2

# Check service type
print(result['service_type1'])  # 'wms', 'wcs', or 'wfs'
```

---

## Return Value

```python
{
    'identical': bool,              # True if exact match
    'same_service_type': bool,      # Both WMS/WCS/WFS
    'common_servers': int,          # Number of shared servers
    'common_server_urls': list,     # URLs of shared servers
    'only_in_file1': list,         # URLs only in file 1
    'only_in_file2': list,         # URLs only in file 2
    'total_connections_file1': int,
    'total_connections_file2': int,
    'service_type1': str,
    'service_type2': str,
}
```

---

## Files Modified

```
ogc2qgis/
├── src/ogc2qgis/
│   ├── __init__.py              ← UPDATED (added compare_configs)
│   └── compare.py               ← NEW
├── tests/
│   └── test_compare.py          ← NEW
└── examples/
    └── compare_configs_example.py ← NEW
```

---

## Run Tests

```bash
cd ogc2qgis
poetry run pytest tests/test_compare.py -v
```

---

## Complete!

The `compare_configs` function is now fully integrated into the ogc2qgis library.

✅ No external dependencies  
✅ Full test coverage  
✅ Usage examples included  
✅ Ready to use immediately
