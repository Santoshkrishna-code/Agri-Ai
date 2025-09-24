#!/usr/bin/env python3
"""
Simple test to verify Roboflow credentials
"""

from inference_sdk import InferenceHTTPClient
import os
from dotenv import load_dotenv
load_dotenv()


# Load credentials
RF_API_KEY = os.getenv("RF_API_KEY")
WORKSPACE_NAME = os.getenv("WORKSPACE_NAME")
RICE_WORKFLOW_ID = os.getenv("RICE_WORKFLOW_ID")
WHEAT_WORKFLOW_ID = os.getenv("WHEAT_WORKFLOW_ID")

print(f"API Key: {RF_API_KEY}")
print(f"Workspace: {WORKSPACE_NAME}")
print(f"Rice Workflow: {RICE_WORKFLOW_ID}")
print(f"Wheat Workflow: {WHEAT_WORKFLOW_ID}")

# Test image URL (publicly accessible)
test_url = "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b"

client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=RF_API_KEY
)

print("\nTesting Rice Workflow...")
try:
    result = client.run_workflow(
        workspace_name=WORKSPACE_NAME,
        workflow_id=RICE_WORKFLOW_ID,
        images={"image": test_url}
    )
    print("✅ Rice workflow succeeded!")
    print(f"Result: {result}")
except Exception as e:
    print(f"❌ Rice workflow failed: {e}")

print("\nTesting Wheat Workflow...")
try:
    result = client.run_workflow(
        workspace_name=WORKSPACE_NAME,
        workflow_id=WHEAT_WORKFLOW_ID,
        images={"image": test_url}
    )
    print("✅ Wheat workflow succeeded!")
    print(f"Result: {result}")
except Exception as e:
    print(f"❌ Wheat workflow failed: {e}")
