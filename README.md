# ConvertHWIND

A Python tool for converting HWIND radar data to GeoJSON format. This tool processes HWIND XML files containing wind data from radar measurements and converts them into GeoJSON format, making it easy to visualize and analyze wind patterns on maps.

## Features

- Converts HWIND XML data to GeoJSON format
- Extracts wind direction and speed data
- Filters valid data points (where ok = 1)
- Preserves sensor metadata
- Supports both file output and in-memory conversion
- Type hints for better IDE support
- Comprehensive error handling

## Installation

This project uses `uv` for dependency management. To install:

```bash
# Clone the repository
git clone https://github.com/yourusername/converhwind.git
cd converhwind

# Install dependencies
uv add deps
```

## Usage

### Basic Usage

```python
from hwind_converter import HwindConverter

# Convert and save to file (automatically uses .geojson extension)
converter = HwindConverter()
geojson_data = converter.convert_to_geojson("path/to/your/hwind_file.hwind")
```

### Advanced Usage

```python
# Convert without saving to file
geojson_data = converter.convert_to_geojson(
    "path/to/your/hwind_file.hwind",
    save_file=False
)

# Convert and save to specific output path
geojson_data = converter.convert_to_geojson(
    "path/to/your/hwind_file.hwind",
    output_path="path/to/output/custom_name.geojson"
)
```

### Command Line Usage

```bash
uv run hwind_converter.py input_file.hwind
```

## Output Format

The tool generates GeoJSON with the following structure:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [longitude, latitude]
      },
      "properties": {
        "hordir": horizontal_direction,
        "horspeed": horizontal_speed
      }
    }
  ],
  "metadata": {
    "sensor": {
      "name": "sensor_name",
      "id": "sensor_id",
      "type": "sensor_type",
      "location": {
        "longitude": sensor_longitude,
        "latitude": sensor_latitude,
        "altitude": sensor_altitude
      }
    },
    "datetime": "measurement_datetime"
  }
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.