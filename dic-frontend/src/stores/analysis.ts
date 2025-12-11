import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type {
  DICAnalysis,
  DICAnalysisStats,
  DICAnalysisSummary,
  DICAnalysisListResponse
} from '@/types/api';
import { apiService } from '@/services/api';

export const useAnalysisStore = defineStore('analysis', () => {
  // State
  const analyses = ref<DICAnalysis[]>([]);
  const currentAnalysis = ref<DICAnalysis | null>(null);
  const stats = ref<DICAnalysisStats | null>(null);
  const summary = ref<DICAnalysisSummary | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Pagination
  const currentPage = ref(1);
  const pageSize = ref(10);
  const totalCount = ref(0);
  const hasNextPage = ref(false);
  const hasPreviousPage = ref(false);

  // Filters
  const statusFilter = ref<string>('');
  const searchQuery = ref<string>('');
  const dateFrom = ref<string>('');
  const dateTo = ref<string>('');
  const hasResultsFilter = ref<boolean | null>(null);

  // Computed
  const completedAnalyses = computed(() =>
    analyses.value.filter(analysis => analysis.status === 'completed')
  );

  const processingAnalyses = computed(() =>
    analyses.value.filter(analysis => analysis.status === 'processing')
  );

  const pendingAnalyses = computed(() =>
    analyses.value.filter(analysis => analysis.status === 'pending')
  );

  const errorAnalyses = computed(() =>
    analyses.value.filter(analysis => analysis.status === 'error')
  );

  // Actions
  async function fetchAnalyses(page = 1) {
    loading.value = true;
    error.value = null;

    try {
      const params: any = {
        page,
        page_size: pageSize.value,
      };

      if (statusFilter.value) params.status = statusFilter.value;
      if (searchQuery.value) params.search = searchQuery.value;
      if (dateFrom.value) params.date_from = dateFrom.value;
      if (dateTo.value) params.date_to = dateTo.value;
      if (hasResultsFilter.value !== null) params.has_results = hasResultsFilter.value;

      const response = await apiService.getAnalyses(params);
      analyses.value = response.data.results;
      totalCount.value = response.data.count;
      currentPage.value = page;
      hasNextPage.value = !!response.data.next;
      hasPreviousPage.value = !!response.data.previous;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch analyses';
      console.error('Error fetching analyses:', err);
    } finally {
      loading.value = false;
    }
  }

  async function fetchAnalysis(id: string) {
    loading.value = true;
    error.value = null;

    try {
      const response = await apiService.getAnalysis(id);
      currentAnalysis.value = response.data;
      return response.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch analysis';
      console.error('Error fetching analysis:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function createAnalysis(analysisData: any) {
    loading.value = true;
    error.value = null;

    try {
      const response = await apiService.createAnalysis(analysisData);
      analyses.value.unshift(response.data); // Add to the beginning of the list
      totalCount.value++;
      return response.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to create analysis';
      console.error('Error creating analysis:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function cancelAnalysis(id: string) {
    try {
      await apiService.cancelAnalysis(id);

      // Update local state
      const analysis = analyses.value.find(a => a.id === id);
      if (analysis) {
        analysis.status = 'cancelled';
      }

      if (currentAnalysis.value?.id === id) {
        currentAnalysis.value.status = 'cancelled';
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to cancel analysis';
      console.error('Error cancelling analysis:', err);
      throw err;
    }
  }

  async function downloadResults(id: string) {
    try {
      const response = await apiService.downloadAnalysisResults(id);

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `dic_results_${id}.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to download results';
      console.error('Error downloading results:', err);
      throw err;
    }
  }

  async function fetchStats() {
    try {
      const response = await apiService.getStats();
      stats.value = response.data;
    } catch (err: any) {
      console.error('Error fetching stats:', err);
    }
  }

  async function fetchSummary() {
    try {
      const response = await apiService.getSummary();
      summary.value = response.data;
    } catch (err: any) {
      console.error('Error fetching summary:', err);
    }
  }

  async function bulkDeleteAnalyses(taskIds: string[]) {
    loading.value = true;
    error.value = null;

    try {
      const response = await apiService.bulkDeleteAnalyses(taskIds);

      // Remove deleted analyses from local state
      analyses.value = analyses.value.filter(a => !taskIds.includes(a.id));
      totalCount.value -= response.data.deleted_count;

      return response.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to delete analyses';
      console.error('Error deleting analyses:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Filter actions
  function setStatusFilter(status: string) {
    statusFilter.value = status;
    fetchAnalyses(1);
  }

  function setSearchQuery(query: string) {
    searchQuery.value = query;
    fetchAnalyses(1);
  }

  function setDateRange(from: string, to: string) {
    dateFrom.value = from;
    dateTo.value = to;
    fetchAnalyses(1);
  }

  function setHasResultsFilter(hasResults: boolean | null) {
    hasResultsFilter.value = hasResults;
    fetchAnalyses(1);
  }

  function clearFilters() {
    statusFilter.value = '';
    searchQuery.value = '';
    dateFrom.value = '';
    dateTo.value = '';
    hasResultsFilter.value = null;
    fetchAnalyses(1);
  }

  // Pagination actions
  function nextPage() {
    if (hasNextPage.value) {
      fetchAnalyses(currentPage.value + 1);
    }
  }

  function previousPage() {
    if (hasPreviousPage.value) {
      fetchAnalyses(currentPage.value - 1);
    }
  }

  function goToPage(page: number) {
    fetchAnalyses(page);
  }

  return {
    // State
    analyses,
    currentAnalysis,
    stats,
    summary,
    loading,
    error,

    // Pagination
    currentPage,
    pageSize,
    totalCount,
    hasNextPage,
    hasPreviousPage,

    // Filters
    statusFilter,
    searchQuery,
    dateFrom,
    dateTo,
    hasResultsFilter,

    // Computed
    completedAnalyses,
    processingAnalyses,
    pendingAnalyses,
    errorAnalyses,

    // Actions
    fetchAnalyses,
    fetchAnalysis,
    createAnalysis,
    cancelAnalysis,
    downloadResults,
    fetchStats,
    fetchSummary,
    bulkDeleteAnalyses,

    // Filter actions
    setStatusFilter,
    setSearchQuery,
    setDateRange,
    setHasResultsFilter,
    clearFilters,

    // Pagination actions
    nextPage,
    previousPage,
    goToPage,
  };
});
