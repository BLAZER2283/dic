// API Types for DIC Analysis

export type DICAnalysisStatus =
  | 'pending'
  | 'processing'
  | 'completed'
  | 'error'
  | 'cancelled';

export interface DICAnalysis {
  id: string;
  name: string;
  status: DICAnalysisStatus;
  status_display: string;

  // Parameters
  subset_size: number;
  step: number;
  max_iter: number;
  min_correlation: number;

  // Images
  image_before: string;
  image_after: string;
  image_before_url?: string;
  image_after_url?: string;

  // Results
  result_json?: any;
  result_image_path?: string;
  original_image_path?: string;
  deformed_image_path?: string;
  displacement_map_path?: string;

  result_image_url?: string;
  original_image_url?: string;
  deformed_image_url?: string;
  displacement_map_url?: string;

  // Statistics
  mean_displacement?: number;
  max_displacement?: number;
  median_displacement?: number;
  std_displacement?: number;
  correlation_quality?: number;
  reliable_points_percentage?: number;

  // Metadata
  created_at: string;
  updated_at: string;
  started_at?: string;
  completed_at?: string;
  processing_time?: number;

  // Errors
  error_message?: string;
  error_traceback?: string;
}

export interface DICAnalysisCreate {
  name: string;
  image_before: File;
  image_after: File;
  subset_size?: number;
  step?: number;
  max_iter?: number;
  min_correlation?: number;
}

export interface DICAnalysisStats {
  overview: {
    total: number;
    completed: number;
    processing: number;
    pending: number;
    error: number;
    cancelled: number;
    success_rate: number;
  };
  processing_stats: {
    avg_processing_time: number;
    total_processing_time: number;
  };
  deformation_stats: {
    avg_max_displacement: number;
    avg_mean_displacement: number;
  };
  recent_tasks: DICAnalysis[];
  timeline: {
    last_24_hours: number;
    last_week: number;
    last_month: number;
  };
}

export interface DICAnalysisSummary {
  total_tasks: number;
  completed_tasks: number;
  success_rate: number;
  latest_tasks: DICAnalysis[];
  processing_tasks: DICAnalysis[];
  tasks_by_status: {
    pending: number;
    processing: number;
    completed: number;
    error: number;
    cancelled: number;
  };
}

export interface DICAnalysisListResponse {
  count: number;
  next?: string;
  previous?: string;
  results: DICAnalysis[];
}

export interface CSRFToken {
  csrfToken: string;
}
