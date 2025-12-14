import axios, { AxiosInstance, AxiosResponse } from 'axios';
import type {
  DICAnalysis,
  DICAnalysisCreate,
  DICAnalysisStats,
  DICAnalysisSummary,
  DICAnalysisListResponse,
  CSRFToken
} from '@/types/api';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: '/api',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to include CSRF token
    this.api.interceptors.request.use(async (config) => {
      if (config.method && ['post', 'put', 'patch', 'delete'].includes(config.method.toLowerCase())) {
        try {
          console.log('DEBUG: Getting CSRF token for request:', config.url);
          const csrfResponse = await this.getCSRFToken();
          const csrfToken = csrfResponse.data.csrfToken;
          console.log('DEBUG: Got CSRF token:', csrfToken ? csrfToken.substring(0, 20) + '...' : 'null');

          // For multipart/form-data, add CSRF token to FormData
          if (config.headers['Content-Type']?.includes('multipart/form-data') && config.data instanceof FormData) {
            console.log('DEBUG: Adding CSRF token to FormData');
            config.data.append('csrfmiddlewaretoken', csrfToken);
          } else {
            // For other requests, add to headers
            config.headers['X-CSRFToken'] = csrfToken;
          }
        } catch (error) {
          console.warn('Failed to get CSRF token:', error);
        }
      }
      return config;
    });

    // Add response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized access
          console.error('Unauthorized access');
        }
        return Promise.reject(error);
      }
    );
  }

  // CSRF Token
  async getCSRFToken(): Promise<AxiosResponse<CSRFToken>> {
    return this.api.get('/get-csrf-token/');
  }

  // DIC Analysis CRUD operations
  async getAnalyses(params?: {
    page?: number;
    page_size?: number;
    status?: string;
    search?: string;
    ordering?: string;
    date_from?: string;
    date_to?: string;
    has_results?: boolean;
  }): Promise<AxiosResponse<DICAnalysisListResponse>> {
    return this.api.get('/analyses/', { params });
  }

  async getAnalysis(id: string): Promise<AxiosResponse<DICAnalysis>> {
    return this.api.get(`/analyses/${id}/`);
  }

  async createAnalysis(data: DICAnalysisCreate): Promise<AxiosResponse<DICAnalysis>> {
    console.log('DEBUG: createAnalysis called with data:', {
      name: data.name,
      image_before: data.image_before?.name,
      image_after: data.image_after?.name,
      subset_size: data.subset_size,
      step: data.step,
      max_iter: data.max_iter,
      min_correlation: data.min_correlation,
      sample_name: data.sample_name,
      material: data.material,
      manufacture: data.manufacture,
      test_date: data.test_date
    });

    // Get CSRF token first
    let csrfToken = '';
    try {
      console.log('DEBUG: Getting CSRF token for analysis creation');
      const csrfResponse = await this.getCSRFToken();
      csrfToken = csrfResponse.data.csrfToken;
      console.log('DEBUG: Got CSRF token:', csrfToken ? csrfToken.substring(0, 20) + '...' : 'null');
    } catch (error) {
      console.warn('Failed to get CSRF token:', error);
    }

    const formData = new FormData();
    formData.append('name', data.name);
    formData.append('image_before', data.image_before);
    formData.append('image_after', data.image_after);

    if (data.subset_size) formData.append('subset_size', data.subset_size.toString());
    if (data.step) formData.append('step', data.step.toString());
    if (data.max_iter) formData.append('max_iter', data.max_iter.toString());
    if (data.min_correlation) formData.append('min_correlation', data.min_correlation.toString());

    // Sample information
    if (data.sample_name) formData.append('sample_name', data.sample_name);
    if (data.material) formData.append('material', data.material);
    if (data.manufacture) formData.append('manufacture', data.manufacture);
    if (data.test_date) formData.append('test_date', data.test_date);

    // Add CSRF token to FormData for multipart requests
    if (csrfToken) {
      formData.append('csrfmiddlewaretoken', csrfToken);
      console.log('DEBUG: Added CSRF token to FormData');
    }

    // Log FormData contents
    console.log('DEBUG: FormData contents:');
    for (let [key, value] of formData.entries()) {
      if (value instanceof File) {
        console.log(`${key}: File(${value.name}, ${value.size} bytes, ${value.type})`);
      } else {
        console.log(`${key}: ${value}`);
      }
    }

    try {
      // Use fetch directly for multipart/form-data with CSRF token
      console.log('DEBUG: Sending request with fetch...');
      const response = await fetch('/api/analyses/', {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': csrfToken
        }
      });

      console.log('DEBUG: Response status:', response.status);

      if (response.ok) {
        const responseData = await response.json();
        console.log('DEBUG: createAnalysis success:', responseData);
        return { data: responseData, status: response.status, statusText: response.statusText, headers: response.headers, config: {} } as AxiosResponse<DICAnalysis>;
      } else {
        const errorText = await response.text();
        console.error('DEBUG: createAnalysis error:', response.status, errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }
    } catch (error) {
      console.error('DEBUG: createAnalysis error:', error);
      throw error;
    }
  }

  async cancelAnalysis(id: string): Promise<AxiosResponse<{ message: string }>> {
    return this.api.post(`/analyses/${id}/cancel/`);
  }

  async downloadAnalysisResults(id: string): Promise<AxiosResponse<Blob>> {
    return this.api.get(`/analyses/${id}/download/`, {
      responseType: 'blob',
    });
  }

  async downloadPDFReport(id: string): Promise<AxiosResponse<Blob>> {
    return this.api.get(`/analyses/${id}/pdf_generate/`, {
      responseType: 'blob',
    });
  }

  async getAnalysisImage(id: string, type: 'displacement' | 'before' | 'after' = 'displacement'): Promise<AxiosResponse<Blob>> {
    return this.api.get(`/analyses/${id}/image/`, {
      params: { type },
      responseType: 'blob',
    });
  }

  async bulkDeleteAnalyses(taskIds: string[]): Promise<AxiosResponse<{ message: string; deleted_count: number }>> {
    return this.api.post('/analyses/bulk_delete/', { task_ids: taskIds });
  }

  // Statistics and summary
  async getStats(): Promise<AxiosResponse<DICAnalysisStats>> {
    return this.api.get('/analyses/stats/');
  }

  async getSummary(): Promise<AxiosResponse<DICAnalysisSummary>> {
    return this.api.get('/analyses/summary/');
  }

  async getRecentAnalyses(): Promise<AxiosResponse<DICAnalysis[]>> {
    return this.api.get('/analyses/recent/');
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;
