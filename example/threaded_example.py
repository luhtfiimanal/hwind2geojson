"""
Example of using HwindConverter in a multi-threaded environment.
This example shows how to process multiple HWIND files concurrently.
"""

import glob
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from hwind2geojson import HwindConverter

def process_file(hwind_file: Path) -> dict:
    """Process a single HWIND file."""
    converter = HwindConverter()
    return converter.convert_to_geojson(
        hwind_file,
        output_path=hwind_file.with_suffix('.geojson')
    )

def main():
    # Get all HWIND files in the current directory
    hwind_files = list(Path('.').glob('*.hwind'))
    if not hwind_files:
        print("No HWIND files found in current directory")
        return
    
    # Process files concurrently using a thread pool
    with ThreadPoolExecutor() as executor:
        # Submit all files for processing
        future_to_file = {
            executor.submit(process_file, f): f 
            for f in hwind_files
        }
        
        # Process results as they complete
        for future in as_completed(future_to_file):
            hwind_file = future_to_file[future]
            try:
                result = future.result()
                print(f"Successfully converted {hwind_file}")
                print(f"Found {len(result['features'])} wind data points")
            except Exception as e:
                print(f"Error processing {hwind_file}: {e}")

if __name__ == '__main__':
    main()
