import axios, { AxiosInstance, AxiosResponse } from 'axios';
import type {
  DICAnalysis,
  DICAnalysisCreate,
  DICAnalysisStats,
  DICAnalysisSummary,
  DICAnalysisListResponse,
  CSRFToken
} from '@/types/api';
import { useAuthStore } from '@/auth/stores/auth.store';

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

    // Add request interceptor to include CSRF token and Bearer token
    this.api.interceptors.request.use(async (config) => {
      // Add Bearer token if available - используем auth store
      const authStore = useAuthStore();
      if (authStore.accessToken) {
        config.headers['Authorization'] = `Bearer ${authStore.accessToken}`;
      }

      if (config.method && ['post', 'put', 'patch', 'delete'].includes(config.method.toLowerCase())) {
        try {
          const csrfResponse = await this.getCSRFToken();
          const csrfToken = csrfResponse.data.csrfToken;

          if (config.headers['Content-Type']?.includes('multipart/form-data') && config.data instanceof FormData) {
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
          // Handle unauthorized access - используем auth store для очистки
          const authStore = useAuthStore();
          authStore.clearAuth();
          window.location.href = '/auth';
        }
        return Promise.reject(error);
      }
    );
  }

  // CSRF Token
  async getCSRFToken(): Promise<AxiosResponse<CSRFToken>> {
    return this.api.get('/auth/get-csrf-token/');
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
    let csrfToken = '';
    try {
      const csrfResponse = await this.getCSRFToken();
      csrfToken = csrfResponse.data.csrfToken;
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
    // Always include min_correlation if it's defined (even if 0)
    if (data.min_correlation !== undefined && data.min_correlation !== null) {
      formData.append('min_correlation', data.min_correlation.toString());
    }

    // Sample information
    if (data.sample_name) formData.append('sample_name', data.sample_name);
    if (data.material) formData.append('material', data.material);
    if (data.manufacture) formData.append('manufacture', data.manufacture);
    if (data.test_date) formData.append('test_date', data.test_date);

    if (csrfToken) {
      formData.append('csrfmiddlewaretoken', csrfToken);
    }

    try {
      const authStore = useAuthStore();
      const headers: Record<string, string> = {
        'X-CSRFToken': csrfToken
      };
      if (authStore.accessToken) {
        headers['Authorization'] = `Bearer ${authStore.accessToken}`;
      }
      const response = await fetch('/api/analyses/', {
        method: 'POST',
        body: formData,
        headers
      });

      if (response.ok) {
        const responseData = await response.json();
        return { data: responseData, status: response.status, statusText: response.statusText, headers: response.headers, config: {} } as AxiosResponse<DICAnalysis>;
      } else {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }
    } catch (error) {
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
