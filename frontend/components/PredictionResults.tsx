import React from 'react'
import { PredictionResponse, Detection } from '@/types/api'
import { CheckCircle, AlertCircle, Clock, Target } from 'lucide-react'

interface PredictionResultsProps {
    prediction: PredictionResponse
}

export default function PredictionResults({ prediction }: PredictionResultsProps) {
    const formatConfidence = (confidence: number): string => {
        return `${(confidence * 100).toFixed(1)}%`
    }

    const formatProcessingTime = (milliseconds: number): string => {
        if (milliseconds < 1000) {
            return `${milliseconds.toFixed(0)}ms`
        }
        return `${(milliseconds / 1000).toFixed(1)}s`
    }

    const getModelColor = (model: string): string => {
        switch (model.toLowerCase()) {
            case 'rice':
                return 'text-green-600 bg-green-50 border-green-200'
            case 'wheat':
                return 'text-amber-600 bg-amber-50 border-amber-200'
            default:
                return 'text-gray-600 bg-gray-50 border-gray-200'
        }
    }

    const getConfidenceColor = (confidence: number): string => {
        if (confidence >= 0.8) return 'text-green-600 bg-green-50'
        if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-50'
        if (confidence >= 0.4) return 'text-orange-600 bg-orange-50'
        return 'text-red-600 bg-red-50'
    }

    const getStatusIcon = (confidence: number) => {
        if (confidence >= 0.7) {
            return <CheckCircle className="w-5 h-5 text-green-600" />
        } else if (confidence >= 0.4) {
            return <AlertCircle className="w-5 h-5 text-yellow-600" />
        } else {
            return <AlertCircle className="w-5 h-5 text-red-600" />
        }
    }

    return (
        <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Analysis Results</h2>
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <Clock className="w-4 h-4" />
                    <span>Analysis Complete</span>
                </div>
            </div>

            {/* Model Selection */}
            <div className="mb-6">
                <div className="flex items-center justify-between mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">Model Selection</h3>
                    <span className={`px-3 py-1 rounded-full border text-sm font-medium ${getModelColor(prediction.chosen_model)}`}>
                        {prediction.chosen_model.charAt(0).toUpperCase() + prediction.chosen_model.slice(1)} Model
                    </span>
                </div>
                <p className="text-gray-600">
                    Selected based on highest confidence score from available models
                </p>
            </div>

            {/* Primary Detection */}
            {prediction.detections.length > 0 ? (
                <div className="mb-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Primary Detection</h3>
                    {prediction.detections.map((detection, index) => (
                        <div key={index} className="border border-gray-200 rounded-lg p-4 mb-3">
                            <div className="flex items-center justify-between mb-3">
                                <div className="flex items-center space-x-2">
                                    {getStatusIcon(detection.confidence)}
                                    <span className="font-medium text-gray-900">{detection.class}</span>
                                </div>
                                <span className={`px-2 py-1 rounded-full text-sm font-medium ${getConfidenceColor(detection.confidence)}`}>
                                    {formatConfidence(detection.confidence)}
                                </span>
                            </div>

                            <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                    <span className="text-gray-500">Position:</span>
                                    <span className="ml-2 font-mono">
                                        ({detection.x.toFixed(0)}, {detection.y.toFixed(0)})
                                    </span>
                                </div>
                                <div>
                                    <span className="text-gray-500">Size:</span>
                                    <span className="ml-2 font-mono">
                                        {detection.width.toFixed(0)} × {detection.height.toFixed(0)}
                                    </span>
                                </div>
                            </div>

                            {/* Confidence bar */}
                            <div className="mt-3">
                                <div className="flex justify-between text-xs text-gray-500 mb-1">
                                    <span>Confidence Level</span>
                                    <span>{formatConfidence(detection.confidence)}</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2">
                                    <div
                                        className={`h-2 rounded-full transition-all duration-300 ${detection.confidence >= 0.8 ? 'bg-green-500' :
                                                detection.confidence >= 0.6 ? 'bg-yellow-500' :
                                                    detection.confidence >= 0.4 ? 'bg-orange-500' : 'bg-red-500'
                                            }`}
                                        style={{ width: `${detection.confidence * 100}%` }}
                                    />
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="mb-6">
                    <div className="border border-gray-200 rounded-lg p-6 text-center">
                        <Target className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">No Detections Found</h3>
                        <p className="text-gray-600">
                            No rice or wheat diseases were detected in this image with sufficient confidence.
                        </p>
                    </div>
                </div>
            )}

            {/* Technical Details */}
            <div className="border-t border-gray-200 pt-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Technical Details</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div className="space-y-2">
                        <div className="flex justify-between">
                            <span className="text-gray-500">Rice Confidence:</span>
                            <span className="font-mono">
                                {formatConfidence(prediction.metadata.rice_confidence)}
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-500">Wheat Confidence:</span>
                            <span className="font-mono">
                                {formatConfidence(prediction.metadata.wheat_confidence)}
                            </span>
                        </div>
                    </div>
                    <div className="space-y-2">
                        <div className="flex justify-between">
                            <span className="text-gray-500">Min Threshold:</span>
                            <span className="font-mono">
                                {formatConfidence(prediction.metadata.min_confidence_threshold)}
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-500">Total Detections:</span>
                            <span className="font-mono">
                                {prediction.detections.length}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}