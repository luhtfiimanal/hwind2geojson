"""
Tests for thread safety of the HWIND converter.
"""

import os
import json
import threading
import time
from pathlib import Path
import pytest
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil
from converhwind import HwindConverter

@pytest.fixture
def sample_hwind_file():
    """Fixture providing path to sample HWIND file."""
    return Path(__file__).parent.parent / "example" / "sample.hwind"

@pytest.fixture
def temp_dir(tmp_path):
    """Fixture providing a temporary directory for test outputs."""
    test_dir = tmp_path / "thread_tests"
    test_dir.mkdir()
    return test_dir

def test_concurrent_same_input_different_outputs(sample_hwind_file, temp_dir):
    """Test multiple threads reading the same input file but writing to different outputs."""
    num_threads = 3
    converter = HwindConverter()
    futures = []
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Submit conversion tasks
        for i in range(num_threads):
            output_file = temp_dir / f"output_{i}.geojson"
            future = executor.submit(
                converter.convert_to_geojson,
                sample_hwind_file,
                output_file
            )
            futures.append((future, output_file))
        
        # Wait for all tasks to complete and verify results
        for future, output_file in futures:
            result = future.result()  # This will raise any exceptions that occurred
            assert output_file.exists()
            
            # Verify file contents
            with open(output_file) as f:
                saved_data = json.load(f)
            assert saved_data == result
            assert saved_data["type"] == "FeatureCollection"

def test_concurrent_same_output(sample_hwind_file, temp_dir):
    """Test multiple threads writing to the same output file."""
    num_threads = 3
    output_file = temp_dir / "shared_output.geojson"
    converter = HwindConverter()
    results = []
    
    def convert_with_delay():
        # Add small random delay to increase chance of concurrent access
        time.sleep(0.01)
        return converter.convert_to_geojson(sample_hwind_file, output_file)
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(convert_with_delay) for _ in range(num_threads)]
        for future in as_completed(futures):
            results.append(future.result())
    
    # Verify the output file exists and is valid
    assert output_file.exists()
    with open(output_file) as f:
        saved_data = json.load(f)
    
    # All results should be identical
    assert all(result == results[0] for result in results)
    assert saved_data == results[0]

def test_concurrent_different_inputs(sample_hwind_file, temp_dir):
    """Test multiple threads processing different input files."""
    num_threads = 3
    converter = HwindConverter()
    
    # Create multiple input files
    input_files = []
    for i in range(num_threads):
        input_file = temp_dir / f"input_{i}.hwind"
        shutil.copy(sample_hwind_file, input_file)
        input_files.append(input_file)
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Submit conversion tasks
        futures = []
        for input_file in input_files:
            output_file = input_file.with_suffix('.geojson')
            future = executor.submit(
                converter.convert_to_geojson,
                input_file,
                output_file
            )
            futures.append((future, output_file))
        
        # Wait for all tasks and verify results
        for future, output_file in futures:
            result = future.result()
            assert output_file.exists()
            
            # Verify file contents
            with open(output_file) as f:
                saved_data = json.load(f)
            assert saved_data == result

def test_concurrent_no_output_file(sample_hwind_file):
    """Test multiple threads converting without saving to file."""
    num_threads = 3
    converter = HwindConverter()
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(
                converter.convert_to_geojson,
                sample_hwind_file,
                save_file=False
            )
            for _ in range(num_threads)
        ]
        
        # All results should be identical
        results = []
        for future in as_completed(futures):
            results.append(future.result())
        assert all(result == results[0] for result in results)
