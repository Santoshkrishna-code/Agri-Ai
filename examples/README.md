# Example Scripts for Agri-AI Inference Service

This directory contains example scripts and utilities for testing and using the Agri-AI Inference Service.

## Files Overview

### test_service.py
**Purpose**: Basic testing and validation of the service  
**Usage**: Test individual endpoints and functionality

```bash
# Test health endpoint
python test_service.py --test-api

# Test with local image file
python test_service.py --test-file path/to/image.jpg

# Test with image URL
python test_service.py --test-url "https://example.com/image.jpg"

# Show curl examples
python test_service.py --curl-examples
```

### batch_process.py
**Purpose**: Process multiple images in parallel  
**Usage**: Batch processing for directories, file lists, or URL lists

```bash
# Process all images in a directory
python batch_process.py --directory /path/to/images --output results.json

# Process images from file list
python batch_process.py --file-list sample_files.txt --output results.csv

# Process images from URL list
python batch_process.py --url-list sample_urls.txt --workers 8
```

### performance_test.py
**Purpose**: Load testing and performance analysis  
**Usage**: Stress test the service under various loads

```bash
# Health check load test
python performance_test.py --test-type health --requests 100 --concurrent 10

# Prediction load test
python performance_test.py --test-type prediction --image-url "https://example.com/test.jpg"

# Comprehensive stress test
python performance_test.py --test-type stress --output stress_results.json
```

## Sample Files

- **sample_files.txt**: Example list of local image file paths
- **sample_urls.txt**: Example list of image URLs for testing

## Dependencies

Some example scripts require additional packages:

```bash
pip install aiohttp  # for performance_test.py async features
```

## Usage Tips

1. **Start the service first**: Make sure the main service is running before using these test scripts
2. **Update file paths**: Modify sample_files.txt with actual paths to your test images
3. **Use valid URLs**: Replace example URLs in sample_urls.txt with actual image URLs
4. **Adjust concurrency**: Start with lower concurrent values and increase based on your system capacity
5. **Save results**: Use the --output option to save results for analysis

## Example Workflow

```bash
# 1. Start the service
python app.py

# 2. Quick health check
python examples/test_service.py --test-api

# 3. Test with a single image
python examples/test_service.py --test-file my_test_image.jpg

# 4. Batch process a directory
python examples/batch_process.py --directory test_images/ --output batch_results.json

# 5. Performance test
python examples/performance_test.py --test-type health --requests 50
```