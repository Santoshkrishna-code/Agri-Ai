'use client'

import React, { useState, useEffect } from 'react'
import { Activity, Leaf, Wheat, Shield, TrendingUp } from 'lucide-react'
import ImageUpload from '../components/ImageUpload'
import PredictionResults from '../components/PredictionResults'
import { PredictionResponse } from '../types/api'
import { apiService } from '../lib/api'
import { Toaster } from 'react-hot-toast'

export default function HomePage() {
    const [prediction, setPrediction] = useState<PredictionResponse | null>(null)
    const [loading, setLoading] = useState(false)
    const [healthStatus, setHealthStatus] = useState<'checking' | 'healthy' | 'error'>('checking')

    useEffect(() => {
        checkHealth()
    }, [])

    const checkHealth = async () => {
        try {
            await apiService.checkHealth()
            setHealthStatus('healthy')
        } catch (error) {
            console.error('Health check failed:', error)
            setHealthStatus('error')
        }
    }

    const handlePrediction = (result: PredictionResponse) => {
        setPrediction(result)
    }

    const getStatusColor = () => {
        switch (healthStatus) {
            case 'healthy': return 'text-green-600 bg-green-50'
            case 'error': return 'text-red-600 bg-red-50'
            default: return 'text-yellow-600 bg-yellow-50'
        }
    }

    const getStatusText = () => {
        switch (healthStatus) {
            case 'healthy': return 'Service Online'
            case 'error': return 'Service Offline'
            default: return 'Checking...'
        }
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-green-50 to-amber-50">
            <Toaster position="top-right" />

            {/* Header */}
            <header className="bg-white shadow-sm border-b">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center py-6">
                        <div className="flex items-center space-x-3">
                            <div className="flex items-center space-x-2">
                                <Leaf className="w-8 h-8 text-green-600" />
                                <Wheat className="w-8 h-8 text-amber-600" />
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900">Agri-AI</h1>
                                <p className="text-sm text-gray-600">Rice & Wheat Disease Detection</p>
                            </div>
                        </div>

                        <div className="flex items-center space-x-3">
                            <div className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor()}`}>
                                <Activity className="w-4 h-4 inline mr-1" />
                                {getStatusText()}
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Hero Section */}
                <div className="text-center mb-12">
                    <h2 className="text-4xl font-bold text-gray-900 mb-4">
                        AI-Powered Crop Disease Detection
                    </h2>
                    <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                        Upload images of rice or wheat crops to detect diseases using advanced machine learning.
                        Get instant analysis with confidence scores and actionable insights.
                    </p>
                </div>

                {/* Features Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                    <div className="bg-white rounded-xl p-6 shadow-sm border">
                        <div className="flex items-center space-x-3 mb-4">
                            <Shield className="w-8 h-8 text-blue-600" />
                            <h3 className="text-lg font-semibold text-gray-900">Dual Model Analysis</h3>
                        </div>
                        <p className="text-gray-600">
                            Specialized models for both rice and wheat crops ensure accurate disease detection
                            with the best model automatically selected.
                        </p>
                    </div>

                    <div className="bg-white rounded-xl p-6 shadow-sm border">
                        <div className="flex items-center space-x-3 mb-4">
                            <TrendingUp className="w-8 h-8 text-green-600" />
                            <h3 className="text-lg font-semibold text-gray-900">High Accuracy</h3>
                        </div>
                        <p className="text-gray-600">
                            Advanced computer vision models trained on extensive agricultural datasets
                            provide reliable disease identification.
                        </p>
                    </div>

                    <div className="bg-white rounded-xl p-6 shadow-sm border">
                        <div className="flex items-center space-x-3 mb-4">
                            <Activity className="w-8 h-8 text-purple-600" />
                            <h3 className="text-lg font-semibold text-gray-900">Instant Results</h3>
                        </div>
                        <p className="text-gray-600">
                            Get immediate analysis results with detailed confidence scores and
                            technical metadata for informed decision making.
                        </p>
                    </div>
                </div>

                {/* Upload Section */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <div>
                        <ImageUpload
                            onPrediction={handlePrediction}
                            loading={loading}
                            setLoading={setLoading}
                        />
                    </div>

                    <div>
                        {prediction ? (
                            <PredictionResults prediction={prediction} />
                        ) : (
                            <div className="bg-white rounded-xl shadow-lg p-8 text-center">
                                <div className="flex justify-center mb-4">
                                    <div className="relative">
                                        <Leaf className="w-16 h-16 text-green-400 opacity-60" />
                                        <Wheat className="w-12 h-12 text-amber-400 opacity-60 absolute -top-2 -right-2" />
                                    </div>
                                </div>
                                <h3 className="text-xl font-semibold text-gray-900 mb-2">Ready for Analysis</h3>
                                <p className="text-gray-600">
                                    Upload an image or provide a URL to get started with AI-powered crop disease detection.
                                </p>

                                <div className="mt-6 pt-6 border-t border-gray-200">
                                    <h4 className="text-sm font-medium text-gray-900 mb-3">Supported Image Formats:</h4>
                                    <div className="flex justify-center space-x-4 text-sm text-gray-600">
                                        <span>JPEG</span>
                                        <span>•</span>
                                        <span>PNG</span>
                                        <span>•</span>
                                        <span>WebP</span>
                                        <span>•</span>
                                        <span>GIF</span>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Instructions */}
                <div className="mt-12 bg-blue-50 rounded-xl p-8">
                    <h3 className="text-xl font-semibold text-blue-900 mb-4">How to Use</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="flex items-start space-x-3">
                            <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                                1
                            </div>
                            <div>
                                <h4 className="font-medium text-blue-900 mb-1">Upload Image</h4>
                                <p className="text-blue-700 text-sm">
                                    Drag and drop an image file or paste an image URL
                                </p>
                            </div>
                        </div>

                        <div className="flex items-start space-x-3">
                            <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                                2
                            </div>
                            <div>
                                <h4 className="font-medium text-blue-900 mb-1">AI Analysis</h4>
                                <p className="text-blue-700 text-sm">
                                    Our models analyze the image for disease indicators
                                </p>
                            </div>
                        </div>

                        <div className="flex items-start space-x-3">
                            <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                                3
                            </div>
                            <div>
                                <h4 className="font-medium text-blue-900 mb-1">View Results</h4>
                                <p className="text-blue-700 text-sm">
                                    Get detailed analysis with confidence scores and insights
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </main>

            {/* Footer */}
            <footer className="bg-white border-t mt-16">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    <div className="text-center text-gray-600">
                        <p>© 2024 Agri-AI. Powered by Roboflow Computer Vision Platform.</p>
                    </div>
                </div>
            </footer>
        </div>
    )
}