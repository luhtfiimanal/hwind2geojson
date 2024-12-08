"""
Example of using HwindConverter in an async environment.
This example shows how to process multiple HWIND files concurrently using asyncio.
"""

import asyncio
from pathlib import Path
from hwind2geojson import HwindConverter

async def process_file(hwind_file: Path) -> dict:
    """Process a single HWIND file asynchronously."""
    converter = HwindConverter()
    # Run the conversion in a thread pool to avoid blocking
    return await asyncio.to_thread(
        converter.convert_to_geojson,
        hwind_file,
        output_path=hwind_file.with_suffix('.geojson')
    )

async def main():
    # Get all HWIND files in the current directory
    hwind_files = list(Path('.').glob('*.hwind'))
    if not hwind_files:
        print("No HWIND files found in current directory")
        return
    
    # Create tasks for all files
    tasks = [process_file(f) for f in hwind_files]
    
    # Process all files concurrently
    try:
        results = await asyncio.gather(*tasks)
        for file, result in zip(hwind_files, results):
            print(f"Successfully converted {file}")
            print(f"Found {len(result['features'])} wind data points")
    except Exception as e:
        print(f"Error processing files: {e}")

if __name__ == '__main__':
    # Run the async main function
    asyncio.run(main())
