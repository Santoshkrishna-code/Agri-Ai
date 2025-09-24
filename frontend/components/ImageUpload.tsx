'use client'

import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, Link2, X, Loader2, Camera } from 'lucide-react'
import { PredictionResponse } from '@/types/api'
import { apiService } from '@/lib/api'
import CameraCapture from './CameraCapture'
import toast from 'react-hot-toast'

interface ImageUploadProps {
    onPrediction: (result: PredictionResponse) => void
    loading: boolean
    setLoading: (loading: boolean) => void
}

export default function ImageUpload({ onPrediction, loading, setLoading }: ImageUploadProps) {
    const [imageUrl, setImageUrl] = useState('')
    const [previewUrl, setPreviewUrl] = useState<string | null>(null)
    const [uploadMethod, setUploadMethod] = useState<'file' | 'url' | 'camera'>('file')

    const onDrop = useCallback(async (acceptedFiles: File[]) => {
        const file = acceptedFiles[0]
        if (!file) return

        // Create preview
        const preview = URL.createObjectURL(file)
        setPreviewUrl(preview)

        // Predict
        setLoading(true)
        try {
            const result = await apiService.predictImageFile(file)
            onPrediction(result)
            toast.success('Image analyzed successfully!')
        } catch (error) {
            console.error('Prediction error:', error)
            toast.error(error instanceof Error ? error.message : 'Failed to analyze image')
        } finally {
            setLoading(false)
        }
    }, [onPrediction, setLoading])

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.webp']
        },
        multiple: false,
        disabled: loading
    })

    const handleUrlSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!imageUrl.trim()) return

        setPreviewUrl(imageUrl)
        setLoading(true)

        try {
            const result = await apiService.predictImage(imageUrl)
            onPrediction(result)
            toast.success('Image analyzed successfully!')
        } catch (error) {
            console.error('Prediction error:', error)
            toast.error(error instanceof Error ? error.message : 'Failed to analyze image')
        } finally {
            setLoading(false)
        }
    }

    const clearImage = () => {
        setPreviewUrl(null)
        setImageUrl('')
        if (previewUrl && previewUrl.startsWith('blob:')) {
            URL.revokeObjectURL(previewUrl)
        }
    }

    return (
        <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="mb-4">
                <div className="flex space-x-4 mb-4">
                    <button
                        onClick={() => setUploadMethod('file')}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${uploadMethod === 'file'
                            ? 'bg-primary-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                    >
                        <Upload className="w-4 h-4 inline mr-2" />
                        Upload File
                    </button>
                    <button
                        onClick={() => setUploadMethod('url')}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${uploadMethod === 'url'
                            ? 'bg-primary-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                    >
                        <Link2 className="w-4 h-4 inline mr-2" />
                        Image URL
                    </button>
                    <button
                        onClick={() => setUploadMethod('camera')}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${uploadMethod === 'camera'
                            ? 'bg-primary-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                    >
                        <Camera className="w-4 h-4 inline mr-2" />
                        Camera
                    </button>
                </div>
            </div>

            {uploadMethod === 'file' ? (
                <div
                    {...getRootProps()}
                    className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer ${isDragActive
                        ? 'border-primary-500 bg-primary-50'
                        : loading
                            ? 'border-gray-200 bg-gray-50 cursor-not-allowed'
                            : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
                        }`}
                >
                    <input {...getInputProps()} />
                    {loading ? (
                        <div className="flex flex-col items-center">
                            <Loader2 className="w-12 h-12 text-primary-600 animate-spin mb-4" />
                            <p className="text-gray-600">Analyzing image...</p>
                        </div>
                    ) : (
                        <div className="flex flex-col items-center">
                            <Upload className="w-12 h-12 text-gray-400 mb-4" />
                            <p className="text-lg font-medium text-gray-900 mb-2">
                                {isDragActive ? 'Drop the image here' : 'Drop an image here, or click to select'}
                            </p>
                            <p className="text-sm text-gray-500">
                                Supports JPEG, PNG, GIF, BMP, WebP (max 10MB)
                            </p>
                        </div>
                    )}
                </div>
            ) : uploadMethod === 'url' ? (
                <form onSubmit={handleUrlSubmit} className="space-y-4">
                    <div>
                        <label htmlFor="imageUrl" className="block text-sm font-medium text-gray-700 mb-2">
                            Image URL
                        </label>
                        <input
                            id="imageUrl"
                            type="url"
                            value={imageUrl}
                            onChange={(e) => setImageUrl(e.target.value)}
                            placeholder="https://example.com/image.jpg"
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                            disabled={loading}
                            required
                        />
                    </div>
                    <button
                        type="submit"
                        disabled={loading || !imageUrl.trim()}
                        className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
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
                </form>
            ) : uploadMethod === 'camera' ? (
                <CameraCapture
                    onPrediction={onPrediction}
                    loading={loading}
                    setLoading={setLoading}
                />
            ) : null}

            {previewUrl && uploadMethod !== 'camera' && (
                <div className="mt-6">
                    <div className="flex justify-between items-center mb-3">
                        <h3 className="text-lg font-medium text-gray-900">Preview</h3>
                        <button
                            onClick={clearImage}
                            className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                    <div className="relative rounded-lg overflow-hidden">
                        <img
                            src={previewUrl}
                            alt="Preview"
                            className="w-full h-64 object-cover"
                            onError={() => {
                                toast.error('Failed to load image preview')
                                setPreviewUrl(null)
                            }}
                        />
                    </div>
                </div>
            )}
        </div>
    )
}