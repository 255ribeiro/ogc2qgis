"""
Example: Using compare_configs function from ogc2qgis library
"""

from ogc2qgis import compare_configs

# Example 1: Compare two QGIS configuration files
print("Example 1: Basic comparison")
print("-" * 50)

result = compare_configs(
    'qgis_wms_connections_v1.xml',
    'qgis_wms_connections_v2.xml'
)

if result['identical']:
    print("✅ Configurations are identical")
elif result['common_servers'] > 0:
    print(f"⚠️  Partial match: {result['common_servers']} common server(s)")
    print(f"   Common URLs: {result['common_server_urls']}")
else:
    print("❌ No common servers found")

# Example 2: Check specific conditions
print("\n\nExample 2: Detailed analysis")
print("-" * 50)

print(f"Service types: {result['service_type1']} vs {result['service_type2']}")
print(f"Total connections: {result['total_connections_file1']} vs {result['total_connections_file2']}")

if result['only_in_file1']:
    print(f"\n📄 Unique to file 1:")
    for url in result['only_in_file1']:
        print(f"   • {url}")

if result['only_in_file2']:
    print(f"\n📄 Unique to file 2:")
    for url in result['only_in_file2']:
        print(f"   • {url}")

# Example 3: Validate deployment
print("\n\nExample 3: Deployment validation")
print("-" * 50)

staging_to_prod = compare_configs('staging.xml', 'production.xml')

if not staging_to_prod['identical']:
    print("⚠️  WARNING: Production differs from staging!")
    
    if staging_to_prod['only_in_file1']:
        print("\n❌ Missing in production:")
        for url in staging_to_prod['only_in_file1']:
            print(f"   {url}")
    
    if staging_to_prod['only_in_file2']:
        print("\n⚠️  Extra in production:")
        for url in staging_to_prod['only_in_file2']:
            print(f"   {url}")
else:
    print("✅ Production matches staging perfectly")

# Example 4: Connection name differences
print("\n\nExample 4: Check connection names")
print("-" * 50)

for conn in result['common_connections']:
    if not conn['same_name']:
        print(f"⚠️  Same server, different names:")
        print(f"   URL: {conn['url']}")
        print(f"   File 1: {conn['file1_name']}")
        print(f"   File 2: {conn['file2_name']}")
