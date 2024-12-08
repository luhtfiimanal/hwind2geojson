"""
Tests for the HWIND converter.
"""

import os
import json
from pathlib import Path
import pytest
from converhwind import HwindConverter

@pytest.fixture
def sample_hwind_file():
    return Path(__file__).parent.parent / "example" / "sample.hwind"

def test_convert_to_geojson(sample_hwind_file, tmp_path):
    """Test basic conversion of HWIND to GeoJSON."""
    output_file = tmp_path / "output.geojson"
    
    # Convert the file
    converter = HwindConverter()
    result = converter.convert_to_geojson(
        sample_hwind_file,
        output_path=output_file
    )
    
    # Check that the output file exists
    assert output_file.exists()
    
    # Verify the GeoJSON structure
    assert result["type"] == "FeatureCollection"
    assert "features" in result
    assert "metadata" in result
    assert "sensor" in result["metadata"]
    
    # Check that features have the correct structure
    for feature in result["features"]:
        assert feature["type"] == "Feature"
        assert "geometry" in feature
        assert feature["geometry"]["type"] == "Point"
        assert len(feature["geometry"]["coordinates"]) == 2
        assert "properties" in feature
        assert "hordir" in feature["properties"]
        assert "horspeed" in feature["properties"]
