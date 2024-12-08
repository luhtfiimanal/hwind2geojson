"""
HWIND data converter module for converting HWIND XML data to GeoJSON format.
"""

import xml.etree.ElementTree as ET
import json
from pathlib import Path
from typing import Union, Dict, Optional
import logging
import threading
from contextlib import contextmanager

@contextmanager
def file_lock(path: Union[str, Path]):
    """Thread-safe file access using a lock per file path."""
    path = str(path)
    if not hasattr(file_lock, '_locks'):
        file_lock._locks = {}
        file_lock._lock = threading.Lock()
    
    with file_lock._lock:
        if path not in file_lock._locks:
            file_lock._locks[path] = threading.Lock()
        lock = file_lock._locks[path]
    
    with lock:
        yield

class HwindConverter:
    """Class for converting HWIND data to GeoJSON format.
    
    This class is thread-safe. Multiple threads can safely call convert_to_geojson
    concurrently, even on the same input/output files, as file operations are protected
    by locks.
    """
    
    file_lock = staticmethod(file_lock)
    
    @staticmethod
    def convert_to_geojson(
        input_path: Union[str, Path], 
        output_path: Optional[Union[str, Path]] = None,
        save_file: bool = True
    ) -> Dict:
        """
        Convert HWIND XML data to GeoJSON format.
        
        This method is thread-safe. Multiple threads can safely call this method
        concurrently, even on the same input/output files.
        
        Args:
            input_path: Path to the input HWIND XML file
            output_path: Optional path for the output GeoJSON file. 
                        If not provided and save_file is True, will use input filename with .geojson extension
            save_file: Whether to save the GeoJSON to a file
            
        Returns:
            dict: The GeoJSON data as a Python dictionary
            
        Raises:
            FileNotFoundError: If input file doesn't exist
            ET.ParseError: If XML parsing fails
            ValueError: If required data is missing in the HWIND file
        """
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
            
        # Parse the XML file with file lock
        with HwindConverter.file_lock(input_path):
            try:
                tree = ET.parse(input_path)
                root = tree.getroot()
            except ET.ParseError as e:
                raise ET.ParseError(f"Failed to parse XML file: {e}")
            
        # Get sensor info
        sensor_info = root.find('.//sensorinfo')
        if sensor_info is None:
            raise ValueError("No sensor information found in HWIND file")
            
        sensor_lon = float(sensor_info.find('lon').text)
        sensor_lat = float(sensor_info.find('lat').text)
        
        # Get the data cells
        table = root.find('.//table1d')
        if table is None:
            raise ValueError("No data table found in HWIND file")
            
        # Get all relevant data arrays
        cells = {
            'ok': table.find(".//cell[@refid='ok']"),
            'lon': table.find(".//cell[@refid='lon']"),
            'lat': table.find(".//cell[@refid='lat']"),
            'hordir': table.find(".//cell[@refid='hordir']"),
            'horspeed': table.find(".//cell[@refid='horspeed']")
        }
        
        # Check if all required cells exist
        missing_cells = [key for key, value in cells.items() if value is None]
        if missing_cells:
            raise ValueError(f"Missing required data cells: {', '.join(missing_cells)}")
        
        # Convert space-separated strings to lists of values
        data = {
            'ok': [int(x) for x in cells['ok'].text.split()],
            'lon': [float(x) for x in cells['lon'].text.split()],
            'lat': [float(x) for x in cells['lat'].text.split()],
            'hordir': [float(x) for x in cells['hordir'].text.split()],
            'horspeed': [float(x) for x in cells['horspeed'].text.split()]
        }
        
        # Create GeoJSON features
        features = []
        for i in range(len(data['ok'])):
            if data['ok'][i] == 1:  # Only include points where ok = 1
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [data['lon'][i], data['lat'][i]]
                    },
                    "properties": {
                        "hordir": data['hordir'][i],
                        "horspeed": data['horspeed'][i]
                    }
                }
                features.append(feature)
        
        # Create the complete GeoJSON structure
        geojson = {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "sensor": {
                    "name": sensor_info.get('name'),
                    "id": sensor_info.get('id'),
                    "type": sensor_info.get('type'),
                    "location": {
                        "longitude": sensor_lon,
                        "latitude": sensor_lat,
                        "altitude": float(sensor_info.find('alt').text)
                    }
                },
                "datetime": root.find('.//data').get('datetimehighaccuracy')
            }
        }
        
        # Save to file if requested
        if save_file:
            if output_path is None:
                output_path = input_path.with_suffix('.geojson')
            else:
                output_path = Path(output_path)
                
            # Ensure directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write with file lock
            with HwindConverter.file_lock(output_path):
                with open(output_path, 'w') as f:
                    json.dump(geojson, f, indent=2)
                logging.info(f"Successfully saved GeoJSON to {output_path}")
            
        return geojson

# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python hwind_converter.py <hwind_file>")
        sys.exit(1)
        
    try:
        converter = HwindConverter()
        result = converter.convert_to_geojson(sys.argv[1])
        print(f"Successfully converted {sys.argv[1]}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
