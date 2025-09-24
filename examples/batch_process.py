#!/usr/bin/env python3
"""
Batch Processing Example for Agri-AI Inference Service
======================================================

This script demonstrates how to process multiple images using the service.

Usage:
    python batch_process.py --directory /path/to/images
    python batch_process.py --file-list images.txt
    python batch_process.py --urls urls.txt
"""

import os
import json
import argparse
import time
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from pathlib import Path


class BatchProcessor:
    """Batch processor for Agri-AI inference"""

    def __init__(self, base_url="http://localhost:5000", max_workers=4):
        self.base_url = base_url
        self.max_workers = max_workers
        self.results = []
        self.session = requests.Session()

    def process_image_file(self, image_path):
        """Process a single image file"""
        try:
            start_time = time.time()

            with open(image_path, 'rb') as f:
                files = {'image': f}
                response = self.session.post(
                    f"{self.base_url}/predict",
                    files=files,
                    timeout=60
                )

            end_time = time.time()
            processing_time = end_time - start_time

            if response.status_code == 200:
                result = response.json()
                return {
                    'image_path': str(image_path),
                    'success': True,
                    'chosen_model': result['chosen_model'],
                    'confidence': result['confidence'],
                    'detection_count': result['detection_count'],
                    'processing_time': processing_time,
                    'metadata': result.get('metadata', {}),
                    'error': None
                }
            else:
                return {
                    'image_path': str(image_path),
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'processing_time': processing_time
                }

        except Exception as e:
            return {
                'image_path': str(image_path),
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time if 'start_time' in locals() else 0
            }

    def process_image_url(self, image_url):
        """Process a single image URL"""
        try:
            start_time = time.time()

            payload = {"image_url": image_url, "use_cache": True}
            response = self.session.post(
                f"{self.base_url}/predict",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=60
            )

            end_time = time.time()
            processing_time = end_time - start_time

            if response.status_code == 200:
                result = response.json()
                return {
                    'image_url': image_url,
                    'success': True,
                    'chosen_model': result['chosen_model'],
                    'confidence': result['confidence'],
                    'detection_count': result['detection_count'],
                    'processing_time': processing_time,
                    'metadata': result.get('metadata', {}),
                    'error': None
                }
            else:
                return {
                    'image_url': image_url,
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'processing_time': processing_time
                }

        except Exception as e:
            return {
                'image_url': image_url,
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time if 'start_time' in locals() else 0
            }

    def process_directory(self, directory_path, extensions=None):
        """Process all images in a directory"""
        if extensions is None:
            extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}

        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        # Find all image files
        image_files = []
        for ext in extensions:
            image_files.extend(directory.glob(f"**/*{ext}"))
            image_files.extend(directory.glob(f"**/*{ext.upper()}"))

        print(f"Found {len(image_files)} image files")

        if not image_files:
            print("No image files found")
            return []

        return self.process_files(image_files)

    def process_file_list(self, file_list_path):
        """Process images from a text file list"""
        with open(file_list_path, 'r') as f:
            file_paths = [line.strip() for line in f if line.strip()]

        # Convert to Path objects and filter existing files
        image_files = []
        for file_path in file_paths:
            path = Path(file_path)
            if path.exists():
                image_files.append(path)
            else:
                print(f"Warning: File not found: {file_path}")

        print(f"Processing {len(image_files)} files from list")
        return self.process_files(image_files)

    def process_url_list(self, url_list_path):
        """Process images from a URL list file"""
        with open(url_list_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip()
                    and line.startswith('http')]

        print(f"Processing {len(urls)} URLs from list")
        return self.process_urls(urls)

    def process_files(self, file_paths):
        """Process multiple image files in parallel"""
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_path = {
                executor.submit(self.process_image_file, path): path
                for path in file_paths
            }

            # Process completed tasks
            for i, future in enumerate(as_completed(future_to_path), 1):
                result = future.result()
                results.append(result)

                # Progress update
                if result['success']:
                    print(f"✅ [{i}/{len(file_paths)}] {result.get('image_path', 'Unknown')}: "
                          f"{result['chosen_model']} ({result['confidence']:.3f})")
                else:
                    print(f"❌ [{i}/{len(file_paths)}] {result.get('image_path', 'Unknown')}: "
                          f"{result['error']}")

        return results

    def process_urls(self, urls):
        """Process multiple image URLs in parallel"""
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_url = {
                executor.submit(self.process_image_url, url): url
                for url in urls
            }

            # Process completed tasks
            for i, future in enumerate(as_completed(future_to_url), 1):
                result = future.result()
                results.append(result)

                # Progress update
                if result['success']:
                    print(f"✅ [{i}/{len(urls)}] {result.get('image_url', 'Unknown')}: "
                          f"{result['chosen_model']} ({result['confidence']:.3f})")
                else:
                    print(f"❌ [{i}/{len(urls)}] {result.get('image_url', 'Unknown')}: "
                          f"{result['error']}")

        return results

    def save_results(self, results, output_file):
        """Save results to JSON or CSV file"""
        if not results:
            print("No results to save")
            return

        output_path = Path(output_file)

        if output_path.suffix.lower() == '.csv':
            self.save_as_csv(results, output_path)
        else:
            self.save_as_json(results, output_path)

        print(f"Results saved to: {output_path}")

    def save_as_json(self, results, output_path):
        """Save results as JSON"""
        with open(output_path, 'w') as f:
            json.dump({
                'summary': self.generate_summary(results),
                'results': results
            }, f, indent=2)

    def save_as_csv(self, results, output_path):
        """Save results as CSV"""
        fieldnames = [
            'image_path', 'image_url', 'success', 'chosen_model',
            'confidence', 'detection_count', 'processing_time', 'error'
        ]

        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for result in results:
                # Flatten the result for CSV
                row = {
                    'image_path': result.get('image_path', ''),
                    'image_url': result.get('image_url', ''),
                    'success': result['success'],
                    'chosen_model': result.get('chosen_model', ''),
                    'confidence': result.get('confidence', ''),
                    'detection_count': result.get('detection_count', ''),
                    'processing_time': result.get('processing_time', ''),
                    'error': result.get('error', '')
                }
                writer.writerow(row)

    def generate_summary(self, results):
        """Generate summary statistics"""
        if not results:
            return {}

        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]

        summary = {
            'total_processed': len(results),
            'successful': len(successful),
            'failed': len(failed),
            'success_rate': len(successful) / len(results) if results else 0
        }

        if successful:
            # Model selection statistics
            model_counts = {}
            confidences = []
            processing_times = []

            for result in successful:
                model = result['chosen_model']
                model_counts[model] = model_counts.get(model, 0) + 1
                confidences.append(result['confidence'])
                processing_times.append(result['processing_time'])

            summary.update({
                'model_selection': model_counts,
                'average_confidence': sum(confidences) / len(confidences),
                'average_processing_time': sum(processing_times) / len(processing_times),
                'total_processing_time': sum(processing_times)
            })

        return summary

    def print_summary(self, results):
        """Print summary statistics"""
        summary = self.generate_summary(results)

        print("\n" + "=" * 50)
        print("📊 BATCH PROCESSING SUMMARY")
        print("=" * 50)
        print(f"Total processed: {summary['total_processed']}")
        print(f"Successful: {summary['successful']}")
        print(f"Failed: {summary['failed']}")
        print(f"Success rate: {summary['success_rate']:.1%}")

        if 'model_selection' in summary:
            print(f"\nModel Selection:")
            for model, count in summary['model_selection'].items():
                percentage = count / summary['successful'] * 100
                print(f"  {model}: {count} ({percentage:.1f}%)")

            print(f"\nPerformance:")
            print(f"  Average confidence: {summary['average_confidence']:.3f}")
            print(
                f"  Average processing time: {summary['average_processing_time']:.2f}s")
            print(
                f"  Total processing time: {summary['total_processing_time']:.2f}s")


def main():
    parser = argparse.ArgumentParser(
        description="Batch processing for Agri-AI Inference Service",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--base-url",
        default="http://localhost:5000",
        help="Base URL of the service"
    )

    parser.add_argument(
        "--directory",
        help="Directory containing images to process"
    )

    parser.add_argument(
        "--file-list",
        help="Text file containing list of image file paths"
    )

    parser.add_argument(
        "--url-list",
        help="Text file containing list of image URLs"
    )

    parser.add_argument(
        "--output",
        help="Output file for results (JSON or CSV)"
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of parallel workers (default: 4)"
    )

    args = parser.parse_args()

    if not any([args.directory, args.file_list, args.url_list]):
        parser.print_help()
        print("\nError: Must specify --directory, --file-list, or --url-list")
        return

    processor = BatchProcessor(args.base_url, args.workers)

    try:
        if args.directory:
            results = processor.process_directory(args.directory)
        elif args.file_list:
            results = processor.process_file_list(args.file_list)
        elif args.url_list:
            results = processor.process_url_list(args.url_list)
        else:
            results = []

        processor.print_summary(results)

        if args.output and results:
            processor.save_results(results, args.output)

    except KeyboardInterrupt:
        print("\n⚠️  Processing interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
