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
git clone https://github.com/luhtfiimanal/hwind2geojson
cd hwind2geojson

# Install dependencies
uv sync

# Run the tool
uv run pytest
```

## Usage

### Installation in Other Projects

You can install this package directly from GitHub:

```bash
uv pip install git+https://github.com/luhtfiimanal/hwind2geojson.git
```

Or install a specific version:
```bash
uv pip install git+https://github.com/luhtfiimanal/hwind2geojson.git@v0.1.0
```

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

## Examples

### Advanced Examples

The package includes examples for both threaded and async usage in the `example` directory:

#### Threaded Example
Process multiple HWIND files concurrently using threads:

```python
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from converhwind import HwindConverter

# Process files concurrently
with ThreadPoolExecutor() as executor:
    hwind_files = Path('.').glob('*.hwind')
    futures = [
        executor.submit(
            HwindConverter().convert_to_geojson,
            hwind_file
        )
        for hwind_file in hwind_files
    ]
```

#### Async Example
Process HWIND files in an async environment:

```python
import asyncio
from pathlib import Path
from converhwind import HwindConverter

async def process_files():
    converter = HwindConverter()
    hwind_files = Path('.').glob('*.hwind')
    
    # Convert files concurrently
    tasks = [
        asyncio.create_task(
            asyncio.to_thread(
                converter.convert_to_geojson,
                hwind_file
            )
        )
        for hwind_file in hwind_files
    ]
    
    return await asyncio.gather(*tasks)

# Run async code
results = asyncio.run(process_files())
```

For complete examples, see:
- [threaded_example.py](example/threaded_example.py): Multi-threaded processing example
- [async_example.py](example/async_example.py): Async processing example

Both examples demonstrate safe concurrent processing of multiple HWIND files.

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