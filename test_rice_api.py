#!/usr/bin/env python3
"""
Test script for the updated Rice Serverless API integration
============================================================

This script tests the new Roboflow Serverless API configuration
using the provided credentials and workflow.
"""

import os
from inference_sdk import InferenceHTTPClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_rice_api():
    """Test the rice detection API with the new configuration"""
    
    # Configuration from your provided API details
    client = InferenceHTTPClient(
        api_url="https://serverless.roboflow.com",
        api_key="9pTsuiQyAxjAJU7XL1sh"
    )
    
    print("🌾 Testing Rice Detection API")
    print("=" * 50)
    print(f"API URL: https://serverless.roboflow.com")
    print(f"Workspace: plant-ai-4q7oj")
    print(f"Workflow ID: custom-workflow-5")
    print(f"API Key: 9pTsuiQyAxjAJU7XL1sh")
    print()
    
    # Test with a sample image (you can replace this with an actual image path)
    test_image = "YOUR_IMAGE.jpg"  # Replace with actual image path
    
    try:
        print(f"🔍 Running inference on: {test_image}")
        
        result = client.run_workflow(
            workspace_name="plant-ai-4q7oj",
            workflow_id="custom-workflow-5",
            images={
                "image": test_image
            },
            use_cache=True  # cache workflow definition for 15 minutes
        )
        
        print("✅ API call successful!")
        print("📊 Result structure:")
        print(f"Type: {type(result)}")
        
        if isinstance(result, dict):
            print("Keys in result:")
            for key in result.keys():
                print(f"  - {key}")
        elif isinstance(result, list):
            print(f"List with {len(result)} items")
            if result:
                print("First item keys:")
                if isinstance(result[0], dict):
                    for key in result[0].keys():
                        print(f"  - {key}")
        
        print("\n📋 Full result:")
        import json
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("Please make sure you have a valid image file path")
        print("or test with a URL instead of a local file path")
        
        # Try with environment variables
        print("\n🔄 Trying with environment variables...")
        try:
            env_result = client.run_workflow(
                workspace_name=os.getenv("WORKSPACE_NAME", "plant-ai-4q7oj"),
                workflow_id=os.getenv("RICE_WORKFLOW_ID", "custom-workflow-5"),
                images={
                    "image": "https://example.com/sample-rice-image.jpg"  # Sample URL
                },
                use_cache=True
            )
            print("✅ Environment variable configuration works!")
        except Exception as env_e:
            print(f"❌ Environment test also failed: {str(env_e)}")

def test_app_integration():
    """Test the app.py integration"""
    print("\n🔧 Testing app.py integration")
    print("=" * 50)
    
    try:
        # Import the app configuration
        from app import Config, create_inference_client
        
        print(f"✅ Configuration loaded:")
        print(f"  - API URL: {Config.RF_API_URL}")
        print(f"  - Workspace: {Config.WORKSPACE_NAME}")
        print(f"  - Rice Workflow: {Config.RICE_WORKFLOW_ID}")
        print(f"  - API Key: {Config.RF_API_KEY[:10]}...")
        
        # Test client creation
        client = create_inference_client()
        print("✅ Client created successfully")
        
        if Config.RF_API_KEY == "YOUR_ROBOFLOW_API_KEY":
            print("⚠️  Warning: Still using placeholder API key")
        else:
            print("✅ Custom API key configured")
            
    except Exception as e:
        print(f"❌ App integration error: {str(e)}")

if __name__ == "__main__":
    test_rice_api()
    test_app_integration()
    
    print("\n" + "=" * 50)
    print("🎯 Next Steps:")
    print("1. Replace 'YOUR_IMAGE.jpg' with an actual image path")
    print("2. Run the Flask app: python app.py")
    print("3. Test the /predict endpoint with an image")
    print("4. The API is now configured for your rice detection workflow!")