# Agri-AI Frontend

A modern React TypeScript frontend for the Agri-AI Rice & Wheat Disease Detection Service.

## Features

- 🌾 **Dual Crop Detection**: Supports both rice and wheat disease detection
- 📤 **Multiple Input Methods**: Upload files or provide image URLs
- 🎯 **Real-time Analysis**: Live predictions with confidence scores
- 📱 **Responsive Design**: Works on desktop and mobile devices
- ⚡ **Fast Performance**: Optimized with Next.js 14 and Tailwind CSS

## Technology Stack

- **Framework**: Next.js 14 with React 18
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Lucide React icons
- **File Upload**: React Dropzone
- **Notifications**: React Hot Toast
- **Deployment**: Vercel

## Getting Started

### Prerequisites

- Node.js 18 or higher
- npm or yarn
- Backend API service running (see parent directory)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env.local
```

3. Update the API URL in `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linting
npm run lint

# Type checking
npm run type-check
```

### Environment Variables

- `NEXT_PUBLIC_API_URL`: Backend API endpoint URL

## Deployment

### Vercel (Recommended)

1. Connect your GitHub repository to Vercel
2. Set the environment variable:
   - `NEXT_PUBLIC_API_URL`: Your production backend URL
3. Deploy automatically on push to main branch

### Manual Deployment

```bash
# Build the application
npm run build

# The built files will be in the .next directory
# Deploy these files to your hosting platform
```

## Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page
├── components/            # React components
│   ├── ImageUpload.tsx    # File/URL upload component
│   └── PredictionResults.tsx # Results display component
├── lib/                   # Utility libraries
│   ├── api.ts            # API service layer
│   └── utils.ts          # Helper functions
├── types/                 # TypeScript definitions
│   └── api.ts            # API response types
├── public/               # Static assets
├── next.config.js        # Next.js configuration
├── tailwind.config.js    # Tailwind CSS configuration
├── tsconfig.json         # TypeScript configuration
└── package.json          # Dependencies and scripts
```

## API Integration

The frontend communicates with the backend via REST API:

- `GET /health` - Health check
- `POST /predict` - Image prediction

### Request Format

```json
{
  "image": "image_url_or_base64",
  "format": "json"
}
```

### Response Format

```json
{
  "chosen_model": "rice|wheat|none",
  "confidence": 0.8456,
  "detection_count": 2,
  "detections": [
    {
      "class": "wheat_rust",
      "confidence": 0.8456,
      "x": 100,
      "y": 150,
      "width": 200,
      "height": 180
    }
  ],
  "metadata": {
    "rice_confidence": 0.2345,
    "wheat_confidence": 0.8456,
    "min_confidence_threshold": 0.4,
    "confidence_margin": 0.02
  }
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License.