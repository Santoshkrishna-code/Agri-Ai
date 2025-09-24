#!/usr/bin/env python3
"""
Quick test with the updated Rice API
===================================

This tests the rice detection API with a sample image URL.
"""

from inference_sdk import InferenceHTTPClient
import json

def test_with_sample_image():
    """Test with a sample rice image URL"""
    
    client = InferenceHTTPClient(
        api_url="https://serverless.roboflow.com",
        api_key="9pTsuiQyAxjAJU7XL1sh"
    )
    
    # Sample rice field image URL (you can replace with any rice image URL)
    test_image_url = "https://images.unsplash.com/photo-1586201375761-83865001e31c?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80"
    
    print("🌾 Testing Rice Detection with Sample Image")
    print("=" * 50)
    print(f"Image URL: {test_image_url}")
    print()
    
    try:
        result = client.run_workflow(
            workspace_name="plant-ai-4q7oj",
            workflow_id="custom-workflow-5",
            images={
                "image": test_image_url
            },
            use_cache=True
        )
        
        print("✅ API call successful!")
        print("\n📊 Full Response:")
        print(json.dumps(result, indent=2))
        
        # Try to extract useful information
        if isinstance(result, list) and result:
            result = result[0]
            
        if isinstance(result, dict):
            predictions = result.get("predictions", {})
            if isinstance(predictions, dict):
                pred_list = predictions.get("predictions", [])
            else:
                pred_list = predictions
                
            print(f"\n🎯 Summary:")
            print(f"Detections found: {len(pred_list) if isinstance(pred_list, list) else 0}")
            
            if isinstance(pred_list, list) and pred_list:
                print("Top detections:")
                for i, pred in enumerate(pred_list[:3]):
                    if isinstance(pred, dict):
                        confidence = pred.get('confidence', pred.get('score', 'N/A'))
                        class_name = pred.get('class', pred.get('label', 'Unknown'))
                        print(f"  {i+1}. {class_name} (confidence: {confidence})")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nThis might be expected if:")
        print("1. The image URL is not accessible")
        print("2. The workflow is not configured for this type of image")
        print("3. The API quota is exceeded")

if __name__ == "__main__":
    test_with_sample_image()