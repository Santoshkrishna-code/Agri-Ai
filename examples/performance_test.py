#!/usr/bin/env python3
"""
Performance Testing Script for Agri-AI Inference Service
========================================================

This script performs load testing and performance analysis.

Usage:
    python performance_test.py --concurrent 10 --requests 100
    python performance_test.py --stress-test
"""

import asyncio
import aiohttp
import time
import statistics
import argparse
import json
from concurrent.futures import ThreadPoolExecutor
import requests


class PerformanceTester:
    """Performance testing for the Agri-AI service"""

    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.results = []

    async def make_request_async(self, session, test_data):
        """Make an async HTTP request"""
        start_time = time.time()

        try:
            if test_data['type'] == 'health':
                async with session.get(f"{self.base_url}/health") as response:
                    await response.text()
                    status = response.status

            elif test_data['type'] == 'url_predict':
                payload = {
                    "image_url": test_data['image_url'],
                    "use_cache": True
                }
                async with session.post(
                    f"{self.base_url}/predict",
                    json=payload
                ) as response:
                    await response.text()
                    status = response.status

            else:
                status = 500  # Unknown test type

            end_time = time.time()

            return {
                'success': 200 <= status < 300,
                'status_code': status,
                'response_time': end_time - start_time,
                'test_type': test_data['type']
            }

        except Exception as e:
            end_time = time.time()
            return {
                'success': False,
                'status_code': 0,
                'response_time': end_time - start_time,
                'error': str(e),
                'test_type': test_data['type']
            }

    async def run_concurrent_test(self, test_data_list, max_concurrent=10):
        """Run concurrent requests"""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def limited_request(session, test_data):
            async with semaphore:
                return await self.make_request_async(session, test_data)

        async with aiohttp.ClientSession() as session:
            tasks = [
                limited_request(session, test_data)
                for test_data in test_data_list
            ]

            results = []
            completed = 0

            for coro in asyncio.as_completed(tasks):
                result = await coro
                results.append(result)
                completed += 1

                if completed % 10 == 0:
                    print(f"Completed {completed}/{len(tasks)} requests")

            return results

    def analyze_results(self, results):
        """Analyze performance results"""
        if not results:
            return {}

        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        response_times = [r['response_time'] for r in successful]

        analysis = {
            'total_requests': len(results),
            'successful_requests': len(successful),
            'failed_requests': len(failed),
            'success_rate': len(successful) / len(results) if results else 0,
            'error_rate': len(failed) / len(results) if results else 0
        }

        if response_times:
            analysis.update({
                'avg_response_time': statistics.mean(response_times),
                'min_response_time': min(response_times),
                'max_response_time': max(response_times),
                'median_response_time': statistics.median(response_times),
                'p95_response_time': self.percentile(response_times, 95),
                'p99_response_time': self.percentile(response_times, 99)
            })

        # Group by test type
        by_type = {}
        for result in results:
            test_type = result['test_type']
            if test_type not in by_type:
                by_type[test_type] = []
            by_type[test_type].append(result)

        analysis['by_test_type'] = {}
        for test_type, type_results in by_type.items():
            type_successful = [r for r in type_results if r['success']]
            type_times = [r['response_time'] for r in type_successful]

            analysis['by_test_type'][test_type] = {
                'total': len(type_results),
                'successful': len(type_successful),
                'success_rate': len(type_successful) / len(type_results) if type_results else 0,
                'avg_response_time': statistics.mean(type_times) if type_times else 0
            }

        return analysis

    @staticmethod
    def percentile(data, percentile):
        """Calculate percentile"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        lower = int(index)
        upper = min(lower + 1, len(sorted_data) - 1)
        weight = index - lower
        return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight

    def print_analysis(self, analysis):
        """Print performance analysis"""
        print("\n" + "=" * 60)
        print("🚀 PERFORMANCE TEST RESULTS")
        print("=" * 60)

        print(f"Total Requests: {analysis['total_requests']}")
        print(f"Successful: {analysis['successful_requests']}")
        print(f"Failed: {analysis['failed_requests']}")
        print(f"Success Rate: {analysis['success_rate']:.1%}")
        print(f"Error Rate: {analysis['error_rate']:.1%}")

        if 'avg_response_time' in analysis:
            print(f"\n📊 Response Time Statistics:")
            print(f"  Average: {analysis['avg_response_time']:.3f}s")
            print(f"  Median:  {analysis['median_response_time']:.3f}s")
            print(f"  Min:     {analysis['min_response_time']:.3f}s")
            print(f"  Max:     {analysis['max_response_time']:.3f}s")
            print(f"  95th %:  {analysis['p95_response_time']:.3f}s")
            print(f"  99th %:  {analysis['p99_response_time']:.3f}s")

        if 'by_test_type' in analysis:
            print(f"\n🔍 By Test Type:")
            for test_type, stats in analysis['by_test_type'].items():
                print(f"  {test_type}:")
                print(f"    Success Rate: {stats['success_rate']:.1%}")
                print(f"    Avg Response: {stats['avg_response_time']:.3f}s")

    async def health_check_load_test(self, num_requests=100, max_concurrent=10):
        """Load test the health check endpoint"""
        print(
            f"🏥 Running health check load test ({num_requests} requests, {max_concurrent} concurrent)")

        test_data = [{'type': 'health'} for _ in range(num_requests)]

        start_time = time.time()
        results = await self.run_concurrent_test(test_data, max_concurrent)
        end_time = time.time()

        total_time = end_time - start_time
        rps = num_requests / total_time

        print(f"⏱️  Total time: {total_time:.2f}s")
        print(f"📈 Requests per second: {rps:.2f}")

        analysis = self.analyze_results(results)
        self.print_analysis(analysis)

        return results, analysis

    async def prediction_load_test(self, image_url, num_requests=50, max_concurrent=5):
        """Load test the prediction endpoint"""
        print(
            f"🔍 Running prediction load test ({num_requests} requests, {max_concurrent} concurrent)")
        print(f"📷 Using image URL: {image_url}")

        test_data = [
            {'type': 'url_predict', 'image_url': image_url}
            for _ in range(num_requests)
        ]

        start_time = time.time()
        results = await self.run_concurrent_test(test_data, max_concurrent)
        end_time = time.time()

        total_time = end_time - start_time
        rps = num_requests / total_time

        print(f"⏱️  Total time: {total_time:.2f}s")
        print(f"📈 Requests per second: {rps:.2f}")

        analysis = self.analyze_results(results)
        self.print_analysis(analysis)

        return results, analysis

    async def stress_test(self, image_url=None):
        """Run a comprehensive stress test"""
        print("🔥 Running comprehensive stress test...")

        # Test 1: Health check burst
        print("\n🏥 Test 1: Health check burst")
        health_results, _ = await self.health_check_load_test(200, 20)

        # Test 2: Moderate prediction load (if URL provided)
        if image_url:
            print("\n🔍 Test 2: Prediction load test")
            pred_results, _ = await self.prediction_load_test(image_url, 30, 3)
        else:
            print("\n⚠️  Skipping prediction test (no image URL provided)")
            pred_results = []

        # Combined analysis
        all_results = health_results + pred_results
        combined_analysis = self.analyze_results(all_results)

        print("\n" + "=" * 60)
        print("🎯 COMBINED STRESS TEST RESULTS")
        print("=" * 60)
        self.print_analysis(combined_analysis)

        return all_results, combined_analysis


async def main():
    parser = argparse.ArgumentParser(
        description="Performance testing for Agri-AI Inference Service"
    )

    parser.add_argument(
        "--base-url",
        default="http://localhost:5000",
        help="Base URL of the service"
    )

    parser.add_argument(
        "--concurrent",
        type=int,
        default=10,
        help="Number of concurrent requests"
    )

    parser.add_argument(
        "--requests",
        type=int,
        default=100,
        help="Total number of requests"
    )

    parser.add_argument(
        "--test-type",
        choices=["health", "prediction", "stress"],
        default="health",
        help="Type of test to run"
    )

    parser.add_argument(
        "--image-url",
        help="Image URL for prediction tests"
    )

    parser.add_argument(
        "--output",
        help="Output file for results (JSON)"
    )

    args = parser.parse_args()

    tester = PerformanceTester(args.base_url)

    try:
        if args.test_type == "health":
            results, analysis = await tester.health_check_load_test(
                args.requests, args.concurrent
            )
        elif args.test_type == "prediction":
            if not args.image_url:
                print("❌ Image URL required for prediction tests (--image-url)")
                return
            results, analysis = await tester.prediction_load_test(
                args.image_url, args.requests, args.concurrent
            )
        elif args.test_type == "stress":
            results, analysis = await tester.stress_test(args.image_url)
        else:
            results, analysis = [], {}

        if args.output:
            output_data = {
                'test_config': {
                    'base_url': args.base_url,
                    'test_type': args.test_type,
                    'concurrent': args.concurrent,
                    'requests': args.requests,
                    'image_url': args.image_url
                },
                'analysis': analysis,
                'results': results
            }

            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"\n💾 Results saved to: {args.output}")

    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
