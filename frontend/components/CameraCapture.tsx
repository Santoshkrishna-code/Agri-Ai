'use client'

import React, { useRef, useState, useCallback, useEffect } from 'react'
import { Camera, CameraOff, Circle, RotateCcw, Loader2 } from 'lucide-react'
import { PredictionResponse } from '../types/api'
import { apiService } from '../lib/api'
import toast from 'react-hot-toast'

interface CameraCaptureProps {
    onPrediction: (result: PredictionResponse) => void
    loading: boolean
    setLoading: (loading: boolean) => void
}

export default function CameraCapture({ onPrediction, loading, setLoading }: CameraCaptureProps) {
    const videoRef = useRef<HTMLVideoElement>(null)
    const canvasRef = useRef<HTMLCanvasElement>(null)
    const streamRef = useRef<MediaStream | null>(null)

    const [isStreamActive, setIsStreamActive] = useState(false)
    const [capturedImage, setCapturedImage] = useState<string | null>(null)
    const [facingMode, setFacingMode] = useState<'user' | 'environment'>('environment')
    const [hasPermission, setHasPermission] = useState<boolean | null>(null)

    // Check camera permissions
    useEffect(() => {
        const checkPermissions = async () => {
            try {
                const result = await navigator.permissions.query({ name: 'camera' as PermissionName })
                setHasPermission(result.state === 'granted')
                result.onchange = () => setHasPermission(result.state === 'granted')
            } catch (error) {
                console.warn('Permission API not supported')
                setHasPermission(null)
            }
        }
        checkPermissions()
    }, [])

    const startCamera = useCallback(async () => {
        try {
            const constraints = {
                video: {
                    facingMode,
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                }
            }

            const stream = await navigator.mediaDevices.getUserMedia(constraints)
            streamRef.current = stream

            if (videoRef.current) {
                videoRef.current.srcObject = stream
                videoRef.current.play()
                setIsStreamActive(true)
                setHasPermission(true)
                toast.success('Camera started successfully')
            }
        } catch (error) {
            console.error('Error starting camera:', error)
            setHasPermission(false)
            toast.error('Failed to access camera. Please check permissions.')
        }
    }, [facingMode])

    const stopCamera = useCallback(() => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop())
            streamRef.current = null
        }
        if (videoRef.current) {
            videoRef.current.srcObject = null
        }
        setIsStreamActive(false)
        setCapturedImage(null)
        toast.success('Camera stopped')
    }, [])

    const captureImage = useCallback(() => {
        if (!videoRef.current || !canvasRef.current) return

        const video = videoRef.current
        const canvas = canvasRef.current
        const context = canvas.getContext('2d')

        if (!context) return

        // Set canvas dimensions to match video
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight

        // Draw video frame to canvas
        context.drawImage(video, 0, 0, canvas.width, canvas.height)

        // Get image data as base64
        const imageData = canvas.toDataURL('image/jpeg', 0.8)
        setCapturedImage(imageData)
        toast.success('Image captured')
    }, [])

    const analyzeImage = useCallback(async () => {
        if (!capturedImage) return

        setLoading(true)
        try {
            const result = await apiService.predictImage(capturedImage)
            onPrediction(result)
            toast.success('Image analyzed successfully!')
        } catch (error) {
            console.error('Prediction error:', error)
            toast.error(error instanceof Error ? error.message : 'Failed to analyze image')
        } finally {
            setLoading(false)
        }
    }, [capturedImage, onPrediction, setLoading])

    const retakePhoto = useCallback(() => {
        setCapturedImage(null)
    }, [])

    const switchCamera = useCallback(() => {
        setFacingMode(prev => prev === 'user' ? 'environment' : 'user')
        if (isStreamActive) {
            stopCamera()
            setTimeout(startCamera, 500) // Small delay to ensure cleanup
        }
    }, [isStreamActive, stopCamera, startCamera])

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop())
            }
        }
    }, [])

    return (
        <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Camera Capture</h3>
                <div className="flex space-x-2">
                    {isStreamActive && (
                        <button
                            onClick={switchCamera}
                            className="px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                            disabled={loading}
                        >
                            <RotateCcw className="w-4 h-4" />
                        </button>
                    )}
                    <button
                        onClick={isStreamActive ? stopCamera : startCamera}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${isStreamActive
                                ? 'bg-red-600 text-white hover:bg-red-700'
                                : 'bg-primary-600 text-white hover:bg-primary-700'
                            }`}
                        disabled={loading}
                    >
                        {isStreamActive ? (
                            <>
                                <CameraOff className="w-4 h-4 inline mr-2" />
                                Stop Camera
                            </>
                        ) : (
                            <>
                                <Camera className="w-4 h-4 inline mr-2" />
                                Start Camera
                            </>
                        )}
                    </button>
                </div>
            </div>

            {hasPermission === false && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                    <p className="text-yellow-800 text-sm">
                        Camera access is required for this feature. Please enable camera permissions in your browser settings.
                    </p>
                </div>
            )}

            <div className="relative">
                {/* Video Stream */}
                {isStreamActive && !capturedImage && (
                    <div className="relative">
                        <video
                            ref={videoRef}
                            className="w-full h-64 md:h-80 object-cover rounded-lg bg-gray-100"
                            autoPlay
                            playsInline
                            muted
                        />
                        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2">
                            <button
                                onClick={captureImage}
                                className="bg-white text-gray-900 p-3 rounded-full shadow-lg hover:shadow-xl transition-shadow"
                                disabled={loading}
                            >
                                <Circle className="w-6 h-6" />
                            </button>
                        </div>
                    </div>
                )}

                {/* Captured Image */}
                {capturedImage && (
                    <div className="relative">
                        <img
                            src={capturedImage}
                            alt="Captured"
                            className="w-full h-64 md:h-80 object-cover rounded-lg"
                        />
                        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex space-x-3">
                            <button
                                onClick={retakePhoto}
                                className="bg-white text-gray-900 px-4 py-2 rounded-lg shadow-lg hover:shadow-xl transition-shadow"
                                disabled={loading}
                            >
                                Retake
                            </button>
                            <button
                                onClick={analyzeImage}
                                className="bg-primary-600 text-white px-4 py-2 rounded-lg shadow-lg hover:bg-primary-700 transition-colors"
                                disabled={loading}
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="w-4 h-4 animate-spin inline mr-2" />
                                        Analyzing...
                                    </>
                                ) : (
                                    'Analyze Image'
                                )}
                            </button>
                        </div>
                    </div>
                )}

                {/* Placeholder when camera is off */}
                {!isStreamActive && !capturedImage && (
                    <div className="w-full h-64 md:h-80 bg-gray-100 rounded-lg flex items-center justify-center">
                        <div className="text-center">
                            <Camera className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                            <p className="text-gray-600 mb-2">Camera not active</p>
                            <p className="text-sm text-gray-500">
                                Click "Start Camera" to begin capturing images
                            </p>
                        </div>
                    </div>
                )}

                {/* Hidden canvas for image capture */}
                <canvas ref={canvasRef} className="hidden" />
            </div>

            {/* Camera Info */}
            {isStreamActive && (
                <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                    <p className="text-sm text-blue-700">
                        <Camera className="w-4 h-4 inline mr-1" />
                        Using {facingMode === 'environment' ? 'rear' : 'front'} camera.
                        Position your crops in the frame and tap capture when ready.
                    </p>
                </div>
            )}
        </div>
    )
}