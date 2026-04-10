"""Main CLI entry point."""

import sys
import argparse
from pathlib import Path
from typing import List

from ogc2qgis import __version__
from ogc2qgis.core import parse_capabilities, detect_service_type, fetch_and_convert


def convert_command(args):
    """Handle convert subcommand."""
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    prefix = args.prefix
    verbose = args.verbose
    
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
            
            if parsed[service_type]:
                output_file = output_dir / f"{prefix}_{service_type}_connections.xml"
                parsed[service_type].save(str(output_file))
                service_files[service_type].append(str(output_file))
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
        print("\n📥 Import into QGIS:")
        print("   Settings → Options → System → Service Connections → Import")
    else:
        print("⚠️  No files generated")


def fetch_command(args):
    """Handle fetch subcommand."""
    url = args.url
    output_dir = Path(args.output_dir)
    verbose = args.verbose
    
    if verbose:
        print(f"🌐 Fetching from: {url}\n")
    
    try:
        results = fetch_and_convert(url, output_dir)
        
        print("\n" + "=" * 60)
        print("✨ FETCH COMPLETE!\n")
        
        for service_type, output_file in results.items():
            if output_file:
                output_path = Path(output_file)
                size = output_path.stat().st_size
                print(f"✓ qgis_{service_type}_connections.xml ({size} bytes)")
        
        print("\n📥 Import into QGIS:")
        print("   Settings → Options → System → Service Connections → Import")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


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
        default='qgis',
        help='Filename prefix (default: qgis)'
    )
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
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    fetch_parser.set_defaults(func=fetch_command)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # Execute command
    args.func(args)


if __name__ == '__main__':
    main()
