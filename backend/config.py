# Configuration loader with environment variables support
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class Config:
    """Centralized configuration management"""

    # Roboflow API Settings
    RF_API_URL = os.getenv("RF_API_URL", "https://serverless.roboflow.com")
    RF_API_KEY = os.getenv("RF_API_KEY", "YOUR_ROBOFLOW_API_KEY")
    WORKSPACE_NAME = os.getenv("WORKSPACE_NAME", "YOUR_WORKSPACE_NAME")

    # Workflow IDs
    RICE_WORKFLOW_ID = os.getenv("RICE_WORKFLOW_ID", "RICE_WORKFLOW_ID")
    WHEAT_WORKFLOW_ID = os.getenv("WHEAT_WORKFLOW_ID", "WHEAT_WORKFLOW_ID")

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

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FILE = os.getenv("LOG_FILE")

    @classmethod
    def validate(cls):
        """Validate required configuration values"""
        errors = []

        if cls.RF_API_KEY == "YOUR_ROBOFLOW_API_KEY":
            errors.append("RF_API_KEY must be set")

        if cls.WORKSPACE_NAME == "YOUR_WORKSPACE_NAME":
            errors.append("WORKSPACE_NAME must be set")

        if cls.RICE_WORKFLOW_ID == "RICE_WORKFLOW_ID":
            errors.append("RICE_WORKFLOW_ID must be set")

        if cls.WHEAT_WORKFLOW_ID == "WHEAT_WORKFLOW_ID":
            errors.append("WHEAT_WORKFLOW_ID must be set")

        return errors
