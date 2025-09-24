#!/usr/bin/env python3
"""
Test script for Agri-AI Inference Service
==========================================

This script demonstrates how to test the service with various scenarios.

Usage:
    python test_service.py --help
    python test_service.py --test-api
    python test_service.py --test-file path/to/image.jpg
    python test_service.py --test-url "https://example.com/image.jpg"
"""

import requests
import json
import argparse
import os
import time
from urllib.parse import urlparse


def test_health_check(base_url="http://localhost:5000"):
    """Test the health check endpoint"""
    print("🏥 Testing health check endpoint...")

    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        response.raise_for_status()

        data = response.json()
        print(f"✅ Health check passed: {data['status']}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_prediction_with_file(image_path, base_url="http://localhost:5000"):
    """Test prediction endpoint with file upload"""
    print(f"📁 Testing file upload with: {image_path}")

    if not os.path.exists(image_path):
        print(f"❌ File not found: {image_path}")
        return False

    try:
        with open(image_path, 'rb') as f:
            files = {'image': f}
            data = {'use_cache': 'true'}

            start_time = time.time()
            response = requests.post(
                f"{base_url}/predict",
                files=files,
                data=data,
                timeout=60
            )
            end_time = time.time()

        response.raise_for_status()
        result = response.json()

        print(f"✅ Prediction completed in {end_time - start_time:.2f} seconds")
        print(f"   Chosen model: {result['chosen_model']}")
        print(f"   Confidence: {result['confidence']:.4f}")
        print(f"   Detections: {result['detection_count']}")

        if result['detections']:
            print("   Top detections:")
            for i, det in enumerate(result['detections'][:3]):  # Show top 3
                class_name = det.get('class', det.get('label', 'Unknown'))
                conf = det.get('confidence', det.get('score', 0))
                print(f"     {i+1}. {class_name} ({conf:.4f})")

        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ File prediction failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_prediction_with_url(image_url, base_url="http://localhost:5000"):
    """Test prediction endpoint with image URL"""
    print(f"🔗 Testing URL prediction with: {image_url}")

    # Validate URL format
    try:
        parsed = urlparse(image_url)
        if not parsed.scheme or not parsed.netloc:
            print("❌ Invalid URL format")
            return False
    except Exception:
        print("❌ Invalid URL format")
        return False

    try:
        payload = {
            "image_url": image_url,
            "use_cache": True
        }

        start_time = time.time()
        response = requests.post(
            f"{base_url}/predict",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        end_time = time.time()

        response.raise_for_status()
        result = response.json()

        print(
            f"✅ URL prediction completed in {end_time - start_time:.2f} seconds")
        print(f"   Chosen model: {result['chosen_model']}")
        print(f"   Confidence: {result['confidence']:.4f}")
        print(f"   Detections: {result['detection_count']}")

        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ URL prediction failed: {e}")
        if hasattr(e, 'response') and e.response:
            try:
                error_data = e.response.json()
                print(
                    f"   Error details: {error_data.get('error', 'Unknown error')}")
            except:
                pass
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def run_comprehensive_test(base_url="http://localhost:5000"):
    """Run a comprehensive test suite"""
    print("🚀 Running comprehensive test suite...")
    print("=" * 50)

    # Test 1: Health check
    health_ok = test_health_check(base_url)
    if not health_ok:
        print("❌ Health check failed - service may not be running")
        return False

    print()

    # Test 2: Error handling - invalid request
    print("🔍 Testing error handling...")
    try:
        response = requests.post(f"{base_url}/predict", json={})
        if response.status_code == 400:
            print("✅ Error handling works correctly")
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")

    print()

    # Test 3: Large file rejection
    print("📦 Testing file size limits...")
    try:
        # Create a small test payload
        response = requests.post(
            f"{base_url}/predict",
            files={'image': ('test.txt', b'not an image', 'text/plain')}
        )
        if response.status_code in [400, 413]:
            print("✅ File validation works correctly")
        else:
            print(f"⚠️  Unexpected response to invalid file")
    except Exception as e:
        print(f"❌ File validation test failed: {e}")

    print("\n" + "=" * 50)
    print("🎯 Test suite completed!")

    return True


def generate_curl_examples():
    """Generate example curl commands"""
    examples = """
🔧 CURL EXAMPLES FOR TESTING
=============================

1. Health Check:
   curl -X GET http://localhost:5000/health

2. File Upload:
   curl -X POST -F "image=@path/to/your/image.jpg" http://localhost:5000/predict

3. Image URL:
   curl -X POST -H "Content-Type: application/json" \
        -d '{"image_url":"https://example.com/image.jpg"}' \
        http://localhost:5000/predict

4. With Cache Disabled:
   curl -X POST -F "image=@image.jpg" -F "use_cache=false" http://localhost:5000/predict

5. Pretty Print Response:
   curl -X POST -F "image=@image.jpg" http://localhost:5000/predict | python -m json.tool
"""
    print(examples)


def main():
    parser = argparse.ArgumentParser(
        description="Test script for Agri-AI Inference Service",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--base-url",
        default="http://localhost:5000",
        help="Base URL of the service (default: http://localhost:5000)"
    )

    parser.add_argument(
        "--test-api",
        action="store_true",
        help="Run comprehensive API tests"
    )

    parser.add_argument(
        "--test-file",
        help="Test prediction with specific image file"
    )

    parser.add_argument(
        "--test-url",
        help="Test prediction with image URL"
    )

    parser.add_argument(
        "--curl-examples",
        action="store_true",
        help="Show curl command examples"
    )

    args = parser.parse_args()

    if args.curl_examples:
        generate_curl_examples()
        return

    if args.test_api:
        run_comprehensive_test(args.base_url)
        return

    if args.test_file:
        test_prediction_with_file(args.test_file, args.base_url)
        return

    if args.test_url:
        test_prediction_with_url(args.test_url, args.base_url)
        return

    # Default: show usage
    parser.print_help()
    print("\nFor curl examples, use: --curl-examples")


if __name__ == "__main__":
    main()
