#!/usr/bin/env python3
"""
Combined Roboflow Inference Service
====================================

A production-ready service that uses Roboflow Serverless Inference SDK to:
- Run rice and wheat detection workflows
- Compare detection confidences to select the best model
- Provide both Flask HTTP API and CLI interface

Author: AI Assistant
Version: 1.0.0
License: MIT
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from inference_sdk import InferenceHTTPClient
import os
import tempfile
import logging
import json
import argparse
from typing import Any, Dict, Tuple, List, Optional

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()


# -----------------------
# CONFIGURATION
# -----------------------


class Config:
    """Configuration class with environment variable support"""

    # Roboflow API Settings
    RF_API_URL = os.getenv("RF_API_URL", "https://serverless.roboflow.com")
    RF_API_KEY = os.getenv(
        "RF_API_KEY", "YOUR_ROBOFLOW_API_KEY")  # <-- REPLACE
    WORKSPACE_NAME = os.getenv(
        "WORKSPACE_NAME", "YOUR_WORKSPACE_NAME")  # <-- REPLACE

    # Workflow IDs - Replace with your actual workflow IDs
    RICE_WORKFLOW_ID = os.getenv(
        "RICE_WORKFLOW_ID", "RICE_WORKFLOW_ID")  # <-- REPLACE
    WHEAT_WORKFLOW_ID = os.getenv(
        "WHEAT_WORKFLOW_ID", "WHEAT_WORKFLOW_ID")  # <-- REPLACE

    # Detection thresholds
    MIN_CONFIDENCE = float(os.getenv("MIN_CONFIDENCE", "0.4"))
    CONFIDENCE_MARGIN = float(os.getenv("CONFIDENCE_MARGIN", "0.02"))

    # Server settings
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "5000"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    # File upload settings
    MAX_CONTENT_LENGTH = int(
        os.getenv("MAX_CONTENT_LENGTH", "16777216"))  # 16MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "webp"}

# -----------------------
# LOGGING SETUP
# -----------------------


def setup_logging():
    """Configure logging with appropriate format and level"""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Create handlers list
    handlers = [logging.StreamHandler()]

    # Add file handler if LOG_FILE is specified
    log_file = os.getenv("LOG_FILE")
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    return logging.getLogger("agri_ai_inference")


logger = setup_logging()

# -----------------------
# ROBOFLOW CLIENT
# -----------------------


def create_inference_client() -> InferenceHTTPClient:
    """Create and configure the Roboflow inference client"""
    if Config.RF_API_KEY == "YOUR_ROBOFLOW_API_KEY":
        logger.warning(
            "Using placeholder API key. Please set RF_API_KEY environment variable.")

    return InferenceHTTPClient(
        api_url=Config.RF_API_URL,
        api_key=Config.RF_API_KEY
    )


client = create_inference_client()

# -----------------------
# CORE INFERENCE FUNCTIONS
# -----------------------


def run_workflow(workflow_id: str, image: str, use_cache: bool = True) -> Dict[str, Any]:
    """
    Run a Roboflow workflow on an image.

    Args:
        workflow_id: The Roboflow workflow ID
        image: Local file path or remote URL
        use_cache: Whether to use Roboflow's caching

    Returns:
        Raw workflow response as dictionary

    Raises:
        Exception: If workflow execution fails
    """
    logger.info(f"Running workflow '{workflow_id}' on image: {image}")

    try:
        response = client.run_workflow(
            workspace_name=Config.WORKSPACE_NAME,
            workflow_id=workflow_id,
            images={"image": image},
            use_cache=use_cache
        )
        logger.debug(f"Workflow '{workflow_id}' completed successfully")
        return response

    except Exception as e:
        logger.error(f"Workflow '{workflow_id}' failed: {str(e)}")
        raise


def extract_max_confidence(result: Any) -> float:
    """
    Extract the maximum detection confidence from a Roboflow response.

    Args:
        result: Raw workflow response

    Returns:
        Maximum confidence score (0.0 if no detections)
    """
    try:
        # Handle list responses (take first item)
        if isinstance(result, list) and result:
            result = result[0]

        if not isinstance(result, dict):
            return 0.0

        # Navigate through common response structures
        predictions_block = result.get("predictions", {})
        if isinstance(predictions_block, dict):
            predictions_list = predictions_block.get("predictions", [])
        else:
            predictions_list = predictions_block if isinstance(
                predictions_block, list) else []

        if not isinstance(predictions_list, list):
            return 0.0

        max_confidence = 0.0
        for prediction in predictions_list:
            if not isinstance(prediction, dict):
                continue

            # Try different confidence field names
            confidence = (
                prediction.get("confidence") or
                prediction.get("score") or
                prediction.get("conf") or
                0.0
            )

            try:
                confidence = float(confidence)
                max_confidence = max(max_confidence, confidence)
            except (ValueError, TypeError):
                continue

        return max_confidence

    except Exception as e:
        logger.exception(f"Error extracting confidence: {e}")
        return 0.0


def extract_predictions(result: Any) -> List[Dict[str, Any]]:
    """
    Extract predictions list from a Roboflow response.

    Args:
        result: Raw workflow response

    Returns:
        List of prediction dictionaries
    """
    try:
        # Handle list responses
        if isinstance(result, list) and result:
            result = result[0]

        if not isinstance(result, dict):
            return []

        predictions_block = result.get("predictions", {})
        if isinstance(predictions_block, dict):
            predictions_list = predictions_block.get("predictions", [])
        else:
            predictions_list = predictions_block if isinstance(
                predictions_block, list) else []

        return predictions_list if isinstance(predictions_list, list) else []

    except Exception as e:
        logger.exception(f"Error extracting predictions: {e}")
        return []


def select_best_model(rice_result: Any, wheat_result: Any) -> Tuple[str, float, Any]:
    """
    Select the best model based on detection confidence.

    Args:
        rice_result: Raw rice workflow response
        wheat_result: Raw wheat workflow response

    Returns:
        Tuple of (chosen_model, max_confidence, chosen_raw_result)
        chosen_model is one of: "rice", "wheat", "none"
    """
    rice_confidence = extract_max_confidence(rice_result)
    wheat_confidence = extract_max_confidence(wheat_result)

    logger.info(
        f"Model confidences - Rice: {rice_confidence:.4f}, Wheat: {wheat_confidence:.4f}")

    # If both are below minimum threshold, return "none"
    if rice_confidence < Config.MIN_CONFIDENCE and wheat_confidence < Config.MIN_CONFIDENCE:
        logger.info("Both models below minimum confidence threshold")
        if rice_confidence >= wheat_confidence:
            return "none", rice_confidence, rice_result
        else:
            return "none", wheat_confidence, wheat_result

    # Apply confidence margin for clearer decisions
    if rice_confidence >= wheat_confidence + Config.CONFIDENCE_MARGIN:
        logger.info("Selected rice model (with margin)")
        return "rice", rice_confidence, rice_result
    elif wheat_confidence >= rice_confidence + Config.CONFIDENCE_MARGIN:
        logger.info("Selected wheat model (with margin)")
        return "wheat", wheat_confidence, wheat_result
    else:
        # Close competition - choose higher confidence
        if rice_confidence >= wheat_confidence:
            logger.info("Selected rice model (close competition)")
            return "rice", rice_confidence, rice_result
        else:
            logger.info("Selected wheat model (close competition)")
            return "wheat", wheat_confidence, wheat_result

# -----------------------
# FLASK APPLICATION
# -----------------------


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH

# Enable CORS for all routes
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])


def allowed_file(filename: str) -> bool:
    """Check if uploaded file has allowed extension"""
    if not filename:
        return False
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def save_uploaded_file(file_storage) -> str:
    """Save uploaded file to temporary location"""
    if not file_storage or not file_storage.filename:
        raise ValueError("No file provided")

    if not allowed_file(file_storage.filename):
        raise ValueError(
            f"File type not allowed. Supported: {', '.join(Config.ALLOWED_EXTENSIONS)}")

    # Create temp file with appropriate extension
    file_ext = os.path.splitext(file_storage.filename)[1] or ".jpg"
    fd, temp_path = tempfile.mkstemp(suffix=file_ext)
    os.close(fd)

    try:
        file_storage.save(temp_path)
        logger.debug(f"Saved uploaded file to: {temp_path}")
        return temp_path
    except Exception as e:
        # Clean up on failure
        try:
            os.remove(temp_path)
        except:
            pass
        raise e


@app.errorhandler(413)
def too_large(e):
    """Handle file too large errors"""
    return jsonify({
        "error": "File too large",
        "max_size_mb": Config.MAX_CONTENT_LENGTH / 1024 / 1024
    }), 413


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "agri-ai-inference",
        "version": "1.0.0"
    })


@app.route("/predict", methods=["POST"])
def predict():
    """
    Main prediction endpoint.

    Accepts:
        - Multipart form data with 'image' file
        - JSON with 'image_url' field

    Returns:
        JSON response with prediction results
    """
    temp_file_path = None

    try:
        # Parse request parameters
        use_cache = True
        image_source = None

        if request.files and 'image' in request.files:
            # Handle file upload
            file = request.files['image']
            temp_file_path = save_uploaded_file(file)
            image_source = temp_file_path

            # Check for cache parameter in form
            cache_param = request.form.get('use_cache', 'true').lower()
            use_cache = cache_param not in ('false', '0', 'no')

        elif request.is_json:
            # Handle JSON request
            data = request.get_json()
            if not data or 'image_url' not in data:
                return jsonify({
                    "error": "JSON request must include 'image_url' field"
                }), 400

            image_source = data['image_url']
            use_cache = data.get('use_cache', True)

        else:
            return jsonify({
                "error": "Request must be multipart/form-data with 'image' file or JSON with 'image_url'"
            }), 400

        if not image_source:
            return jsonify({"error": "No image provided"}), 400

        logger.info(f"Processing prediction request for image: {image_source}")

        # Run both workflows
        try:
            rice_result = run_workflow(
                Config.RICE_WORKFLOW_ID, image_source, use_cache)
            wheat_result = run_workflow(
                Config.WHEAT_WORKFLOW_ID, image_source, use_cache)
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return jsonify({
                "error": "Workflow execution failed",
                "details": str(e)
            }), 500

        # Select best model
        chosen_model, max_confidence, chosen_result = select_best_model(
            rice_result, wheat_result)

        # Extract predictions from chosen result
        predictions = extract_predictions(chosen_result)

        # Build response
        response = {
            "chosen_model": chosen_model,
            "confidence": round(max_confidence, 4),
            "detections": predictions,
            "detection_count": len(predictions),
            "raw": chosen_result,
            "metadata": {
                "rice_confidence": round(extract_max_confidence(rice_result), 4),
                "wheat_confidence": round(extract_max_confidence(wheat_result), 4),
                "min_confidence_threshold": Config.MIN_CONFIDENCE,
                "confidence_margin": Config.CONFIDENCE_MARGIN
            }
        }

        logger.info(
            f"Prediction completed. Chosen model: {chosen_model}, Confidence: {max_confidence:.4f}")
        return jsonify(response)

    except ValueError as e:
        logger.warning(f"Client error: {e}")
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        logger.exception("Unexpected error during prediction")
        return jsonify({
            "error": "Internal server error",
            "details": str(e) if Config.DEBUG else "Please check logs"
        }), 500

    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                logger.debug(f"Cleaned up temp file: {temp_file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temp file: {e}")

# -----------------------
# CLI INTERFACE
# -----------------------


def predict_from_cli(image_path: str, output_format: str = "summary") -> None:
    """
    Run prediction from command line.

    Args:
        image_path: Path to image file
        output_format: Output format ("summary", "json", "detailed")
    """
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        return

    try:
        print(f"Running inference on: {image_path}")
        print("=" * 50)

        # Run both workflows
        rice_result = run_workflow(Config.RICE_WORKFLOW_ID, image_path)
        wheat_result = run_workflow(Config.WHEAT_WORKFLOW_ID, image_path)

        # Select best model
        chosen_model, max_confidence, chosen_result = select_best_model(
            rice_result, wheat_result)

        # Extract predictions
        predictions = extract_predictions(chosen_result)

        if output_format == "json":
            # Full JSON output
            output = {
                "chosen_model": chosen_model,
                "confidence": max_confidence,
                "detections": predictions,
                "raw": chosen_result
            }
            print(json.dumps(output, indent=2))

        elif output_format == "detailed":
            # Detailed output
            print(
                f"Rice confidence: {extract_max_confidence(rice_result):.4f}")
            print(
                f"Wheat confidence: {extract_max_confidence(wheat_result):.4f}")
            print(f"Chosen model: {chosen_model}")
            print(f"Max confidence: {max_confidence:.4f}")
            print(f"Detection count: {len(predictions)}")
            print("\nPredictions:")
            for i, pred in enumerate(predictions):
                conf = pred.get('confidence', pred.get('score', 'N/A'))
                class_name = pred.get('class', pred.get('label', 'Unknown'))
                print(f"  {i+1}. {class_name} (confidence: {conf})")
            print("\nRaw result:")
            print(json.dumps(chosen_result, indent=2))

        else:
            # Summary output (default)
            print(f"Chosen model: {chosen_model}")
            print(f"Confidence: {max_confidence:.4f}")
            print(f"Detections found: {len(predictions)}")
            if predictions:
                print("Top detection:")
                top_pred = max(predictions, key=lambda p: p.get(
                    'confidence', p.get('score', 0)))
                conf = top_pred.get('confidence', top_pred.get('score', 'N/A'))
                class_name = top_pred.get(
                    'class', top_pred.get('label', 'Unknown'))
                print(f"  - {class_name} (confidence: {conf})")

    except Exception as e:
        print(f"Error during prediction: {e}")
        logger.exception("CLI prediction failed")

# -----------------------
# MAIN ENTRY POINT
# -----------------------


def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(
        description="Agri-AI Inference Service - Rice & Wheat Detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start web server
  python app.py

  # Test single image
  python app.py --image sample.jpg

  # Get detailed output
  python app.py --image sample.jpg --output detailed

  # Get JSON output
  python app.py --image sample.jpg --output json

  # Start server on different port
  python app.py --port 8080
        """
    )

    # CLI mode options
    parser.add_argument(
        "--image",
        help="Path to image file for CLI prediction mode"
    )
    parser.add_argument(
        "--output",
        choices=["summary", "json", "detailed"],
        default="summary",
        help="Output format for CLI mode (default: summary)"
    )

    # Server mode options
    parser.add_argument(
        "--host",
        default=Config.HOST,
        help=f"Host to bind server to (default: {Config.HOST})"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=Config.PORT,
        help=f"Port to bind server to (default: {Config.PORT})"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )

    args = parser.parse_args()

    # Validate configuration
    if Config.RF_API_KEY == "YOUR_ROBOFLOW_API_KEY":
        print(
            "⚠️  Warning: Using placeholder API key. Set RF_API_KEY environment variable.")

    if Config.WORKSPACE_NAME == "YOUR_WORKSPACE_NAME":
        print("⚠️  Warning: Using placeholder workspace name. Set WORKSPACE_NAME environment variable.")

    if args.image:
        # CLI mode
        predict_from_cli(args.image, args.output)
    else:
        # Server mode
        print(f"🚀 Starting Agri-AI Inference Service")
        print(f"📡 Server: http://{args.host}:{args.port}")
        print(f"🏥 Health check: http://{args.host}:{args.port}/health")
        print(f"🔍 Prediction endpoint: http://{args.host}:{args.port}/predict")
        print(f"📊 Min confidence: {Config.MIN_CONFIDENCE}")
        print(f"🎯 Confidence margin: {Config.CONFIDENCE_MARGIN}")
        print("=" * 50)

        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug or Config.DEBUG
        )


if __name__ == "__main__":
    main()
