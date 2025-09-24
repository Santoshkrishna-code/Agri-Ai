// API Types
export interface PredictionRequest {
    image_url?: string;
    use_cache?: boolean;
}

export interface Detection {
    class: string;
    class_id: number;
    confidence: number;
    detection_id: string;
    height: number;
    width: number;
    x: number;
    y: number;
    parent_id: string;
}

export interface Metadata {
    confidence_margin: number;
    min_confidence_threshold: number;
    rice_confidence: number;
    wheat_confidence: number;
    processing_time_ms?: number;
    selected_model?: string;
    workflow_id?: string;
    image_width?: number;
    image_height?: number;
}

export interface PredictionResponse {
    chosen_model: 'rice' | 'wheat' | 'none';
    confidence: number;
    detection_count: number;
    detections: Detection[];
    metadata: Metadata;
    raw: any;
}

export interface HealthResponse {
    service: string;
    status: string;
    version: string;
}

// Component Types
export interface UploadState {
    isUploading: boolean;
    isPredicting: boolean;
    error: string | null;
}

export interface ImagePreview {
    file: File;
    url: string;
}

export interface PredictionHistory {
    id: string;
    timestamp: Date;
    imageUrl: string;
    result: PredictionResponse;
    processingTime: number;
}

// API Error Response
export interface ApiError {
    error: string;
    details?: string;
}