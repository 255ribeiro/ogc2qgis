"""Main CLI entry point."""

import sys
import argparse
from pathlib import Path
from typing import List

from ogc2qgis import __version__
from ogc2qgis.core import parse_capabilities, detect_service_type, fetch_and_convert
from ogc2qgis.compare import compare_configs, compare_web, compare_ip


def convert_command(args):
    """Handle convert subcommand."""
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    verbose = args.verbose
    prefix = args.prefix
    qlr_mode = 'only' if args.qlr_only else ('include' if args.qlr_include else None)

    # Track results by service type
    service_files = {'wms': [], 'wcs': [], 'wfs': []}
    
    for file_path in args.files:
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            continue
        
        if verbose:
            print(f"🔍 Analyzing {file_path}...")
        
        service_type = detect_service_type(file_path)
        
        if service_type is None:
            print(f"⚠️  {file_path}: Unknown service type - skipping")
            continue
        
        if verbose:
            print(f"✅ {file_path}: {service_type.upper()}")
        
        # Parse and save
        try:
            parsed = parse_capabilities(file_path)
            parser = parsed[service_type]

            if parser is None:
                if verbose:
                    print(f"⚠️  {file_path}: No {service_type.upper()} data found - skipping")
                continue

            # Skip if no meaningful data was extracted
            if service_type == 'wms':
                has_data = bool(parser.server_url or parser.layers)
            elif service_type == 'wcs':
                has_data = bool(parser.server_url or parser.coverages)
            else:  # wfs
                has_data = bool(parser.server_url or parser.features)

            if not has_data:
                if verbose:
                    print(f"⚠️  {file_path}: No {service_type.upper()} data found - skipping")
                continue

            base_name = prefix if prefix else file_path.stem

            if qlr_mode != 'only':
                output_file = output_dir / f"{base_name}_{service_type}2qgis.xml"
                parser.save(str(output_file))
                service_files[service_type].append(str(output_file))

            if qlr_mode in ('include', 'only'):
                qlr_file = output_dir / f"{base_name}_{service_type}2qgis.qlr"
                parser.save_qlr(str(qlr_file))
                service_files.setdefault(f'{service_type}_qlr', []).append(str(qlr_file))
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("✨ CONVERSION COMPLETE!\n")
    
    generated_files = []
    for service_type, files in service_files.items():
        if files:
            # Use the last file for each service type
            output_file = Path(files[-1])
            if output_file.exists():
                size = output_file.stat().st_size
                print(f"✓ {output_file.name} ({size} bytes)")
                generated_files.append(output_file)
    
    if generated_files:
        has_xml = any(f.suffix == '.xml' for f in generated_files)
        has_qlr = any(f.suffix == '.qlr' for f in generated_files)
        if has_xml:
            print("\n📥 Import connections into QGIS:")
            print("   Settings → Options → System → Service Connections → Import")
        if has_qlr:
            print("\n📂 Import grouped layers into QGIS:")
            print("   Layer → Add from Layer Definition File (.qlr)")
    else:
        print("⚠️  No files generated")


def fetch_command(args):
    """Handle fetch subcommand."""
    url = args.url
    output_dir = Path(args.output_dir)
    verbose = args.verbose
    qlr_mode = 'only' if args.qlr_only else ('include' if args.qlr_include else None)

    if verbose:
        print(f"🌐 Fetching from: {url}\n")

    try:
        results = fetch_and_convert(url, output_dir, base_name=args.prefix, qlr_mode=qlr_mode)
        
        print("\n" + "=" * 60)
        print("✨ FETCH COMPLETE!\n")
        
        has_xml = has_qlr = False
        for service_type, output_file in results.items():
            if output_file:
                output_path = Path(output_file)
                size = output_path.stat().st_size
                print(f"✓ {output_path.name} ({size} bytes)")
                if output_path.suffix == '.qlr':
                    has_qlr = True
                else:
                    has_xml = True

        if has_xml:
            print("\n📥 Import connections into QGIS:")
            print("   Settings → Options → System → Service Connections → Import")
        if has_qlr:
            print("\n📂 Import grouped layers into QGIS:")
            print("   Layer → Add from Layer Definition File (.qlr)")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def compare_command(args):
    """Handle compare subcommand."""
    if args.comp_ip:
        _compare_ip_command(args)
    elif args.comp_web:
        _compare_web_command(args)
    else:
        _compare_files_command(args)


def _compare_ip_command(args):
    """Compare two URLs by resolving their hostnames to IPs."""
    url1, url2 = args.file1, args.file2

    print("=" * 70)
    print("OGC Service IP Comparison")
    print("=" * 70)
    print(f"\nURL 1: {url1}")
    print(f"URL 2: {url2}")

    try:
        result = compare_ip(url1, url2)

        print(f"\nHost 1: {result['host1']}")
        if result['error1']:
            print(f"  ❌ DNS error: {result['error1']}")
        else:
            for ip in result['ips1']:
                print(f"  → {ip}")

        print(f"\nHost 2: {result['host2']}")
        if result['error2']:
            print(f"  ❌ DNS error: {result['error2']}")
        else:
            for ip in result['ips2']:
                print(f"  → {ip}")

        if result['common_ips']:
            print(f"\nCommon IPs: {', '.join(result['common_ips'])}")

        print("\n" + "=" * 70)

        if result['identical']:
            print("✅ IDENTICAL: Same hostname and same IP addresses")
            sys.exit(0)
        elif result['same_host']:
            print("✅ SAME HOST: Identical hostname (same IPs implied)")
            sys.exit(0)
        elif result['same_ip']:
            print("⚠️  SAME IP: Different hostnames but resolve to a common IP")
            sys.exit(1)
        else:
            print("❌ DIFFERENT: Hostnames resolve to different IP addresses")
            sys.exit(2)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def _compare_web_command(args):
    """Compare two live OGC service URLs."""
    url1, url2 = args.file1, args.file2
    service_type = args.service_type

    print("=" * 70)
    print("OGC Web Service Comparison")
    print("=" * 70)
    print(f"\nURL 1: {url1}")
    print(f"URL 2: {url2}")
    if service_type:
        print(f"Service type: {service_type.upper()}")
    print("\nFetching GetCapabilities...")

    try:
        result = compare_web(url1, url2, service_type)

        if result['verdict'] == 'error':
            for key in ('info1', 'info2'):
                info = result[key]
                if info['error']:
                    print(f"\n❌ {info['url']}: {info['error']}")
            sys.exit(1)

        i1, i2 = result['info1'], result['info2']

        print(f"\nService type:    {i1['service_type'].upper()} / {i2['service_type'].upper()}")
        print(f"Reported URL 1:  {i1['server_url'] or '(none)'}")
        print(f"Reported URL 2:  {i2['server_url'] or '(none)'}")
        print(f"Service name 1:  {i1['service_name']}")
        print(f"Service name 2:  {i2['service_name']}")
        print(f"\nLayers URL 1:    {len(i1['layers'])}")
        print(f"Layers URL 2:    {len(i2['layers'])}")
        print(f"Common layers:   {len(result['common_layers'])}")
        print(f"Layer overlap:   {result['layer_overlap_pct']}%")

        if result['only_in_url1']:
            print(f"\nOnly in URL 1 ({len(result['only_in_url1'])}):")
            for name in result['only_in_url1'][:10]:
                print(f"  • {name}")
            if len(result['only_in_url1']) > 10:
                print(f"  ... and {len(result['only_in_url1']) - 10} more")

        if result['only_in_url2']:
            print(f"\nOnly in URL 2 ({len(result['only_in_url2'])}):")
            for name in result['only_in_url2'][:10]:
                print(f"  • {name}")
            if len(result['only_in_url2']) > 10:
                print(f"  ... and {len(result['only_in_url2']) - 10} more")

        print("\n" + "=" * 70)
        verdict = result['verdict']
        if verdict == 'identical':
            print("✅ IDENTICAL: Same server URL, name, and layer set")
            sys.exit(0)
        elif verdict == 'same_server':
            print("⚠️  SAME SERVER: Same reported URL but different name or layers")
            sys.exit(1)
        else:
            print("❌ DIFFERENT: URLs point to different servers")
            sys.exit(2)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def _compare_files_command(args):
    """Compare two local QGIS config XML files."""
    file1 = Path(args.file1)
    file2 = Path(args.file2)

    if not file1.exists():
        print(f"❌ File not found: {file1}")
        sys.exit(1)

    if not file2.exists():
        print(f"❌ File not found: {file2}")
        sys.exit(1)

    try:
        result = compare_configs(file1, file2)

        print("=" * 70)
        print("QGIS Configuration Comparison")
        print("=" * 70)

        print(f"\nFile 1: {result['file1']}")
        print(f"File 2: {result['file2']}")

        print(f"\nService Type: {result['service_type1'].upper()} vs {result['service_type2'].upper()}")

        if not result['same_service_type']:
            print("⚠️  WARNING: Different service types!")
            sys.exit(2)

        print(f"\nConnections:")
        print(f"  File 1: {result['total_connections_file1']} server(s)")
        print(f"  File 2: {result['total_connections_file2']} server(s)")

        print(f"\n✅ Common Servers: {result['common_servers']}")

        if result['common_connections']:
            print("\nCommon server details:")
            for conn in result['common_connections']:
                print(f"  • {conn['url']}")
                print(f"    File 1 name: {conn['file1_name']}")
                print(f"    File 2 name: {conn['file2_name']}")
                if not conn['same_name']:
                    print(f"    ⚠️  Different names!")

        if result['only_in_file1']:
            print(f"\n📄 Only in File 1 ({len(result['only_in_file1'])} server(s)):")
            for url in result['only_in_file1']:
                print(f"  • {url}")

        if result['only_in_file2']:
            print(f"\n📄 Only in File 2 ({len(result['only_in_file2'])} server(s)):")
            for url in result['only_in_file2']:
                print(f"  • {url}")

        print("\n" + "=" * 70)

        if result['identical']:
            print("✅ IDENTICAL: Both files point to the exact same server(s)")
            sys.exit(0)
        elif result['common_servers'] > 0:
            print(f"⚠️  PARTIAL MATCH: {result['common_servers']} common server(s) found")
            sys.exit(1)
        else:
            print("❌ NO MATCH: No common servers found")
            sys.exit(2)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def _add_qlr_args(subparser):
    """Add --qlr-include / --qlr-only as a mutually exclusive group."""
    group = subparser.add_mutually_exclusive_group()
    group.add_argument(
        '--qlr-include',
        action='store_true',
        dest='qlr_include',
        help='Generate both XML connection file and .qlr layer definition',
    )
    group.add_argument(
        '--qlr-only',
        action='store_true',
        dest='qlr_only',
        help='Generate only the .qlr layer definition (skip XML connection file)',
    )


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='ogc2qgis',
        description='Convert OGC Web Services to QGIS configurations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert local file
  ogc2qgis convert capabilities.xml
  
  # Convert multiple files
  ogc2qgis convert ows.xml ows_wcs.xml ows_wfs.xml
  
  # Fetch from URL
  ogc2qgis fetch https://geoservicos.inde.gov.br/geoserver/BAPSalvador/ows
  
  # Compare two QGIS configs
  ogc2qgis compare file1.xml file2.xml
  
  # Custom output directory
  ogc2qgis convert capabilities.xml -o /path/to/output
        """
    )
    
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Convert command
    convert_parser = subparsers.add_parser(
        'convert',
        help='Convert local capabilities files'
    )
    convert_parser.add_argument(
        'files',
        nargs='+',
        help='One or more capabilities XML files'
    )
    convert_parser.add_argument(
        '-o', '--output-dir',
        default='.',
        help='Output directory (default: current directory)'
    )
    convert_parser.add_argument(
        '-p', '--prefix',
        default=None,
        help='Filename prefix (default: input filename stem)'
    )
    _add_qlr_args(convert_parser)
    convert_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    convert_parser.set_defaults(func=convert_command)

    # Fetch command
    fetch_parser = subparsers.add_parser(
        'fetch',
        help='Fetch capabilities from URL and convert'
    )
    fetch_parser.add_argument(
        'url',
        help='Base URL of OGC service'
    )
    fetch_parser.add_argument(
        '-o', '--output-dir',
        default='.',
        help='Output directory (default: current directory)'
    )
    fetch_parser.add_argument(
        '-p', '--prefix',
        default=None,
        help='Filename prefix (default: last URL path segment)'
    )
    _add_qlr_args(fetch_parser)
    fetch_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    fetch_parser.set_defaults(func=fetch_command)
    
    # Compare command
    compare_parser = subparsers.add_parser(
        'compare',
        help='Compare two QGIS configuration files or two live OGC service URLs'
    )
    compare_parser.add_argument(
        'file1',
        help='First QGIS config file, or first OGC service URL (with --comp_web)'
    )
    compare_parser.add_argument(
        'file2',
        help='Second QGIS config file, or second OGC service URL (with --comp_web)'
    )
    compare_parser.add_argument(
        '--comp_web',
        action='store_true',
        help='Compare two live OGC service URLs by fetching their GetCapabilities'
    )
    compare_parser.add_argument(
        '--comp_ip',
        action='store_true',
        help='Compare two URLs by resolving their hostnames to IP addresses'
    )
    compare_parser.add_argument(
        '--service-type',
        choices=['wms', 'wcs', 'wfs'],
        default=None,
        dest='service_type',
        help='Force a specific service type for --comp_web (default: auto-detect)'
    )
    compare_parser.set_defaults(func=compare_command)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # Execute command
    args.func(args)


if __name__ == '__main__':
    main()
