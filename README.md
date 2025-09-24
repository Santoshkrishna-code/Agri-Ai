# Agri-AI Inference Service

A production-ready Python service that uses Roboflow Serverless Inference SDK to run rice and wheat detection workflows, automatically selecting the best model based on detection confidence.

**🌾 UPDATED**: Now configured with the latest Rice Detection API using Roboflow Serverless Hosted API with workflow ID `custom-workflow-5`.

## Features

- 🌾 **Rice Detection Focus**: Primary rice detection using workflow `custom-workflow-5`
- 🎯 **Smart Model Selection**: Automatically chooses the model with highest confidence
- 🚀 **Flask HTTP API**: RESTful API with file upload and URL support
- 💻 **CLI Interface**: Command-line interface for testing and batch processing
- ⚙️ **Configurable Thresholds**: Adjustable confidence and margin settings
- 📊 **Comprehensive Logging**: Detailed logging with configurable levels
- 🔒 **Production Ready**: Error handling, validation, and security features

## Quick Start

### 1. Installation

```bash
# Clone or download the project
cd Agri-Ai

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy the example environment file and fill in your Roboflow credentials:

```bash
copy .env.example .env
```

Edit `.env` file with your actual values:

```env
RF_API_KEY=your_actual_api_key_here
WORKSPACE_NAME=your_workspace_name
RICE_WORKFLOW_ID=your_rice_workflow_id
WHEAT_WORKFLOW_ID=your_wheat_workflow_id
```

### 3. Quick Test

```bash
# Test with CLI (replace with your image path)
python app.py --image path/to/your/image.jpg

# Start the web server
python app.py
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `RF_API_KEY` | Your Roboflow API key | - | ✅ |
| `WORKSPACE_NAME` | Your Roboflow workspace name | - | ✅ |
| `RICE_WORKFLOW_ID` | Rice detection workflow ID | - | ✅ |
| `WHEAT_WORKFLOW_ID` | Wheat detection workflow ID | - | ✅ |
| `MIN_CONFIDENCE` | Minimum confidence threshold | 0.4 | ❌ |
| `CONFIDENCE_MARGIN` | Margin for model selection | 0.02 | ❌ |
| `HOST` | Server host | 0.0.0.0 | ❌ |
| `PORT` | Server port | 5000 | ❌ |
| `DEBUG` | Enable debug mode | false | ❌ |
| `LOG_LEVEL` | Logging level | INFO | ❌ |

### Getting Your Roboflow Credentials

1. **API Key**: 
   - Go to [Roboflow](https://roboflow.com)
   - Navigate to Settings → Roboflow API
   - Copy your API key

2. **Workspace Name**: 
   - Found in your Roboflow dashboard URL
   - Example: `https://app.roboflow.com/your-workspace-name`

3. **Workflow IDs**: 
   - Navigate to your deployed workflows
   - Copy the workflow IDs from the deployment page

## API Documentation

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "agri-ai-inference",
  "version": "1.0.0"
}
```

### Prediction Endpoint

```http
POST /predict
```

**Request Options:**

#### Option 1: File Upload (Multipart Form Data)

```bash
curl -X POST \
  -F "image=@path/to/image.jpg" \
  -F "use_cache=true" \
  http://localhost:5000/predict
```

#### Option 2: Image URL (JSON)

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/image.jpg", "use_cache": true}' \
  http://localhost:5000/predict
```

**Response:**
```json
{
  "chosen_model": "rice",
  "confidence": 0.8542,
  "detections": [
    {
      "class": "rice_blast",
      "confidence": 0.8542,
      "x": 320,
      "y": 240,
      "width": 150,
      "height": 100
    }
  ],
  "detection_count": 1,
  "raw": { /* Full Roboflow response */ },
  "metadata": {
    "rice_confidence": 0.8542,
    "wheat_confidence": 0.2341,
    "min_confidence_threshold": 0.4,
    "confidence_margin": 0.02
  }
}
```

**Response Fields:**

- `chosen_model`: Selected model ("rice", "wheat", or "none")
- `confidence`: Highest detection confidence score
- `detections`: Array of detection objects from chosen model
- `detection_count`: Number of detections found
- `raw`: Complete raw response from chosen workflow
- `metadata`: Additional information about the decision process

## CLI Usage

### Basic Usage

```bash
# Run prediction on single image
python app.py --image sample.jpg

# Get detailed output
python app.py --image sample.jpg --output detailed

# Get JSON output
python app.py --image sample.jpg --output json
```

### Output Formats

- **summary** (default): Brief summary of results
- **detailed**: Full breakdown including both model confidences
- **json**: Complete JSON response

### Examples

```bash
# Summary output
$ python app.py --image rice_sample.jpg
Chosen model: rice
Confidence: 0.8542
Detections found: 3
Top detection:
  - rice_blast (confidence: 0.8542)

# Detailed output
$ python app.py --image rice_sample.jpg --output detailed
Rice confidence: 0.8542
Wheat confidence: 0.2341
Chosen model: rice
Max confidence: 0.8542
Detection count: 3
Predictions:
  1. rice_blast (confidence: 0.8542)
  2. leaf_spot (confidence: 0.7123)
  3. healthy (confidence: 0.6534)
```

## Model Selection Logic

The service uses the following logic to select the best model:

1. **Run both workflows** on the input image
2. **Extract maximum confidence** from each workflow's detections
3. **Apply selection rules**:
   - If both models are below `MIN_CONFIDENCE` → return "none"
   - If one model exceeds the other by `CONFIDENCE_MARGIN` → choose that model
   - Otherwise → choose the model with higher confidence

### Configuration Examples

```env
# Conservative selection (requires clear winner)
MIN_CONFIDENCE=0.5
CONFIDENCE_MARGIN=0.1

# Permissive selection (accepts lower confidence)
MIN_CONFIDENCE=0.3
CONFIDENCE_MARGIN=0.0
```

## Deployment

### Local Development

```bash
# Development server with auto-reload
python app.py --debug

# Custom host and port
python app.py --host 127.0.0.1 --port 8080
```

### Production Deployment

#### Using Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

#### Using Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

Build and run:

```bash
docker build -t agri-ai-inference .
docker run -p 5000:5000 --env-file .env agri-ai-inference
```

### Environment Variables for Production

```bash
# Production settings
export RF_API_KEY="your_actual_api_key"
export WORKSPACE_NAME="your_workspace"
export RICE_WORKFLOW_ID="your_rice_workflow_id"
export WHEAT_WORKFLOW_ID="your_wheat_workflow_id"
export LOG_LEVEL="WARNING"
export DEBUG="false"

# Optional: Enable file logging
export LOG_FILE="/var/log/agri-ai/app.log"
```

## Error Handling

The service includes comprehensive error handling:

### Client Errors (4xx)

- **400 Bad Request**: Invalid request format or missing required fields
- **413 Payload Too Large**: Uploaded file exceeds size limit (16MB default)

### Server Errors (5xx)

- **500 Internal Server Error**: Workflow execution failures or unexpected errors

### Example Error Responses

```json
{
  "error": "File type not allowed. Supported: png, jpg, jpeg, gif, bmp, webp"
}
```

```json
{
  "error": "Workflow execution failed",
  "details": "Invalid API key or workspace name"
}
```

## Logging

The service provides detailed logging with configurable levels:

### Log Levels

- **DEBUG**: Detailed debugging information
- **INFO**: General operational messages
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical errors

### Log Configuration

```env
# Console logging only
LOG_LEVEL=INFO

# Enable file logging
LOG_LEVEL=DEBUG
LOG_FILE=/var/log/agri-ai/app.log
```

## Security Considerations

### API Key Security

- **Never commit** API keys to version control
- Use environment variables or secure secret management
- Consider rotating API keys regularly

### Input Validation

- File type validation (images only)
- File size limits (16MB default)
- URL validation for remote images

### Production Security

- Use HTTPS in production
- Implement rate limiting
- Add authentication if needed
- Monitor for suspicious activity

## Troubleshooting

### Common Issues

#### 1. "Using placeholder API key" Warning

**Problem**: The service starts but shows API key warning.

**Solution**: Set the `RF_API_KEY` environment variable or update `.env` file.

#### 2. Workflow Execution Failed

**Problem**: API returns 500 error with workflow execution failure.

**Solutions**:
- Verify API key is correct
- Check workspace name and workflow IDs
- Ensure workflows are deployed and active
- Check Roboflow service status

#### 3. Low or No Detections

**Problem**: Service returns "none" for most images.

**Solutions**:
- Lower `MIN_CONFIDENCE` threshold
- Verify input images match training data
- Check workflow configuration in Roboflow

#### 4. File Upload Issues

**Problem**: File uploads fail with various errors.

**Solutions**:
- Check file size (must be under 16MB)
- Verify file format (PNG, JPG, etc.)
- Ensure proper Content-Type headers

### Debug Mode

Enable debug mode for additional information:

```bash
python app.py --debug
```

Or set environment variable:

```env
DEBUG=true
```

## Development

### Project Structure

```
Agri-Ai/
├── app.py                 # Main application file
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment file
├── README.md             # This file
├── tests/                # Test files (optional)
└── examples/             # Example scripts and images
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Ensure code passes linting
6. Submit a pull request

### Code Quality

```bash
# Format code
black app.py

# Check for issues
flake8 app.py

# Run tests
pytest tests/
```

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review Roboflow documentation
3. Create an issue in the project repository

## Changelog

### Version 1.0.0
- Initial release
- Rice and wheat detection workflows
- Flask HTTP API
- CLI interface
- Comprehensive logging and error handling
