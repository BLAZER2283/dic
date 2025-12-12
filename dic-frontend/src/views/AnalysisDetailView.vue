<template>
  <div class="analysis-detail">
    <!-- Header -->
    <v-row class="mb-6">
      <v-col cols="12">
        <div class="d-flex align-center justify-space-between flex-wrap">
          <div class="d-flex align-center">
            <v-btn
              variant="text"
              @click="$router.go(-1)"
              class="me-4"
              prepend-icon="mdi-arrow-left"
            >
              Back
            </v-btn>
            <div>
              <h1 class="text-h4 font-weight-bold mb-2">{{ analysis?.name || 'Loading...' }}</h1>
              <p class="text-body-1 text-grey-darken-1">
                DIC Analysis Details
              </p>
            </div>
          </div>

          <div class="d-flex gap-2 flex-wrap" v-if="analysis">
            <v-chip
              :color="getStatusColor(analysis.status)"
              variant="flat"
              class="me-2"
            >
              {{ analysis.status_display }}
            </v-chip>

            <v-btn
              v-if="analysis.status === 'completed'"
              color="primary"
              variant="outlined"
              @click="downloadResults"
              prepend-icon="mdi-download"
              :loading="downloading"
              class="me-2"
            >
              Download Results
            </v-btn>

            <v-btn
              v-if="analysis.status === 'completed'"
              color="success"
              variant="outlined"
              @click="downloadPDFReport"
              prepend-icon="mdi-file-pdf-box"
              :loading="downloadingPDF"
            >
              Download PDF Report
            </v-btn>

            <v-btn
              v-if="analysis.status === 'processing' || analysis.status === 'pending'"
              color="error"
              variant="outlined"
              @click="cancelAnalysis"
              prepend-icon="mdi-cancel"
            >
              Cancel Analysis
            </v-btn>

            <v-btn
              variant="outlined"
              @click="refreshAnalysis"
              prepend-icon="mdi-refresh"
              :loading="loading"
            >
              Refresh
            </v-btn>
          </div>
        </div>
      </v-col>
    </v-row>

    <!-- Loading State -->
    <div v-if="loading && !analysis" class="text-center py-12">
      <v-progress-circular
        indeterminate
        size="64"
        color="primary"
        class="mb-4"
      />
      <div class="text-h6">Loading analysis details...</div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-12">
      <v-icon size="64" color="error" class="mb-4">mdi-alert-circle</v-icon>
      <div class="text-h6 text-error mb-4">{{ error }}</div>
      <v-btn color="primary" @click="loadAnalysis">
        Try Again
      </v-btn>
    </div>

    <!-- Analysis Content -->
    <div v-else-if="analysis">
      <!-- Overview Cards -->
      <v-row class="mb-6">
        <v-col cols="12" md="3">
          <v-card>
            <v-card-text class="text-center">
              <v-icon size="48" color="primary" class="mb-2">mdi-calendar</v-icon>
              <div class="text-h6">{{ formatDate(analysis.created_at) }}</div>
              <div class="text-caption text-grey-darken-1">Created</div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="3">
          <v-card>
            <v-card-text class="text-center">
              <v-icon size="48" color="warning" class="mb-2">mdi-timer-outline</v-icon>
              <div class="text-h6">
                {{ analysis.processing_time ? `${analysis.processing_time.toFixed(1)}s` : '-' }}
              </div>
              <div class="text-caption text-grey-darken-1">Processing Time</div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="3">
          <v-card>
            <v-card-text class="text-center">
              <v-icon size="48" color="success" class="mb-2">mdi-gauge</v-icon>
              <div class="text-h6">
                {{ analysis.max_displacement ? analysis.max_displacement.toFixed(4) : '-' }}
              </div>
              <div class="text-caption text-grey-darken-1">Max Displacement</div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="3">
          <v-card>
            <v-card-text class="text-center">
              <v-icon size="48" color="info" class="mb-2">mdi-percent</v-icon>
              <div class="text-h6">
                {{ analysis.reliable_points_percentage ? `${analysis.reliable_points_percentage}%` : '-' }}
              </div>
              <div class="text-caption text-grey-darken-1">Reliable Points</div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Sample Information -->
      <v-row class="mb-6" v-if="analysis.sample_name || analysis.material || analysis.manufacturer || analysis.test_date">
        <v-col cols="12">
          <v-card>
            <v-card-title>
              <v-icon left>mdi-flask-outline</v-icon>
              Sample Information
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12" md="3" v-if="analysis.sample_name">
                  <div class="text-caption text-grey-darken-1">Sample Name</div>
                  <div class="text-body-1">{{ analysis.sample_name }}</div>
                </v-col>
                <v-col cols="12" md="3" v-if="analysis.material">
                  <div class="text-caption text-grey-darken-1">Material</div>
                  <div class="text-body-1">{{ analysis.material }}</div>
                </v-col>
                <v-col cols="12" md="3" v-if="analysis.manufacturer">
                  <div class="text-caption text-grey-darken-1">Manufacturer</div>
                  <div class="text-body-1">{{ analysis.manufacturer }}</div>
                </v-col>
                <v-col cols="12" md="3" v-if="analysis.test_date">
                  <div class="text-caption text-grey-darken-1">Test Date</div>
                  <div class="text-body-1">{{ formatDate(analysis.test_date) }}</div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Parameters -->
      <v-row class="mb-6">
        <v-col cols="12">
          <v-card>
            <v-card-title>
              <v-icon left>mdi-cog-outline</v-icon>
              Analysis Parameters
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="6" md="3">
                  <div class="text-body-1 font-weight-bold">Subset Size</div>
                  <div class="text-h6 text-primary">{{ analysis.subset_size }}</div>
                </v-col>
                <v-col cols="6" md="3">
                  <div class="text-body-1 font-weight-bold">Step</div>
                  <div class="text-h6 text-primary">{{ analysis.step }}</div>
                </v-col>
                <v-col cols="6" md="3">
                  <div class="text-body-1 font-weight-bold">Max Iterations</div>
                  <div class="text-h6 text-primary">{{ analysis.max_iter }}</div>
                </v-col>
                <v-col cols="6" md="3">
                  <div class="text-body-1 font-weight-bold">Min Correlation</div>
                  <div class="text-h6 text-primary">{{ analysis.min_correlation }}</div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Results Section -->
      <v-row v-if="analysis.status === 'completed'">
        <v-col cols="12">
          <v-card>
            <v-card-title>
              <v-icon left>mdi-chart-line</v-icon>
              Analysis Results
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="6" md="3">
                  <div class="text-body-1 font-weight-bold">Mean Displacement</div>
                  <div class="text-h6 text-success">
                    {{ analysis.mean_displacement ? analysis.mean_displacement.toFixed(4) : '-' }}
                  </div>
                </v-col>
                <v-col cols="6" md="3">
                  <div class="text-body-1 font-weight-bold">Median Displacement</div>
                  <div class="text-h6 text-success">
                    {{ analysis.median_displacement ? analysis.median_displacement.toFixed(4) : '-' }}
                  </div>
                </v-col>
                <v-col cols="6" md="3">
                  <div class="text-body-1 font-weight-bold">Std Deviation</div>
                  <div class="text-h6 text-warning">
                    {{ analysis.std_displacement ? analysis.std_displacement.toFixed(4) : '-' }}
                  </div>
                </v-col>
                <v-col cols="6" md="3">
                  <div class="text-body-1 font-weight-bold">Correlation Quality</div>
                  <div class="text-h6 text-info">
                    {{ analysis.correlation_quality ? analysis.correlation_quality.toFixed(4) : '-' }}
                  </div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Images Section -->
      <v-row class="mb-6">
        <v-col cols="12">
          <v-card>
            <v-card-title>
              <v-icon left>mdi-image-outline</v-icon>
              Images
            </v-card-title>
            <v-card-text>
              <v-row>
                <!-- Before Image -->
                <v-col cols="12" md="6">
                  <div class="text-h6 mb-4">Reference Image (Before)</div>
                  <v-img
                    v-if="analysis.image_before_url"
                    :src="analysis.image_before_url"
                    max-height="400"
                    contain
                    class="rounded border"
                  >
                    <template #placeholder>
                      <div class="d-flex align-center justify-center fill-height">
                        <v-progress-circular indeterminate color="primary" />
                      </div>
                    </template>
                  </v-img>
                  <div v-else class="text-center py-8 text-grey-darken-1">
                    <v-icon size="48" class="mb-2">mdi-image-off</v-icon>
                    <div>Image not available</div>
                  </div>
                </v-col>

                <!-- After Image -->
                <v-col cols="12" md="6">
                  <div class="text-h6 mb-4">Deformed Image (After)</div>
                  <v-img
                    v-if="analysis.image_after_url"
                    :src="analysis.image_after_url"
                    max-height="400"
                    contain
                    class="rounded border"
                  >
                    <template #placeholder>
                      <div class="d-flex align-center justify-center fill-height">
                        <v-progress-circular indeterminate color="primary" />
                      </div>
                    </template>
                  </v-img>
                  <div v-else class="text-center py-8 text-grey-darken-1">
                    <v-icon size="48" class="mb-2">mdi-image-off</v-icon>
                    <div>Image not available</div>
                  </div>
                </v-col>
              </v-row>

              <!-- Displacement Map -->
              <v-row v-if="analysis.status === 'completed' && analysis.displacement_map_url" class="mt-6">
                <v-col cols="12">
                  <div class="text-h6 mb-4">Displacement Map</div>
                  <v-img
                    :src="analysis.displacement_map_url"
                    max-height="400"
                    contain
                    class="rounded border"
                  >
                    <template #placeholder>
                      <div class="d-flex align-center justify-center fill-height">
                        <v-progress-circular indeterminate color="primary" />
                      </div>
                    </template>
                  </v-img>
                  <div class="text-body-2 text-grey-darken-1 mt-2">
                    This map shows the displacement field calculated from the DIC analysis.
                    Color intensity represents displacement magnitude.
                  </div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Processing Status -->
      <v-row v-if="analysis.status === 'processing'">
        <v-col cols="12">
          <v-card color="warning" dark>
            <v-card-text class="text-center py-8">
              <v-progress-circular
                indeterminate
                size="64"
                class="mb-4"
              />
              <div class="text-h6 mb-2">Analysis in Progress</div>
              <div class="text-body-1">
                Your DIC analysis is currently being processed. This may take several minutes.
              </div>
              <v-btn
                variant="outlined"
                @click="refreshAnalysis"
                class="mt-4"
                :loading="loading"
              >
                Check Status
              </v-btn>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Error Display -->
      <v-row v-if="analysis.status === 'error'">
        <v-col cols="12">
          <v-card color="error" dark>
            <v-card-text class="py-6">
              <div class="d-flex align-center mb-4">
                <v-icon size="32" class="me-3">mdi-alert-circle</v-icon>
                <div class="text-h6">Analysis Failed</div>
              </div>
              <div class="text-body-1" v-if="analysis.error_message">
                {{ analysis.error_message }}
              </div>
              <div class="text-body-2 text-grey-lighten-2" v-else>
                The analysis encountered an error. Please check your input images and parameters.
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Cancelled Status -->
      <v-row v-if="analysis.status === 'cancelled'">
        <v-col cols="12">
          <v-card color="grey-darken-1" dark>
            <v-card-text class="text-center py-8">
              <v-icon size="64" class="mb-4">mdi-cancel</v-icon>
              <div class="text-h6 mb-2">Analysis Cancelled</div>
              <div class="text-body-1">
                This analysis was cancelled before completion.
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAnalysisStore } from '@/stores/analysis'
import type { DICAnalysis } from '@/types/api'

const route = useRoute()
const analysisStore = useAnalysisStore()

// Reactive data
const analysis = ref<DICAnalysis | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const downloading = ref(false)
const downloadingPDF = ref(false)

// Methods
const getStatusColor = (status: string) => {
  switch (status) {
    case 'completed': return 'success'
    case 'processing': return 'warning'
    case 'error': return 'error'
    case 'cancelled': return 'grey'
    default: return 'primary'
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString()
}

const loadAnalysis = async () => {
  const id = route.params.id as string
  if (!id) return

  loading.value = true
  error.value = null

  try {
    analysis.value = await analysisStore.fetchAnalysis(id)
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to load analysis'
    console.error('Error loading analysis:', err)
  } finally {
    loading.value = false
  }
}

const refreshAnalysis = () => {
  loadAnalysis()
}

const cancelAnalysis = async () => {
  if (!analysis.value) return

  try {
    await analysisStore.cancelAnalysis(analysis.value.id)
    await loadAnalysis() // Refresh data
  } catch (error) {
    console.error('Failed to cancel analysis:', error)
  }
}

const downloadResults = async () => {
  if (!analysis.value) return

  downloading.value = true
  try {
    await analysisStore.downloadResults(analysis.value.id)
  } catch (error) {
    console.error('Failed to download results:', error)
  } finally {
    downloading.value = false
  }
}

const downloadPDFReport = async () => {
  if (!analysis.value) return

  downloadingPDF.value = true
  try {
    await analysisStore.downloadPDFReport(analysis.value.id)
  } catch (error) {
    console.error('Failed to download PDF report:', error)
  } finally {
    downloadingPDF.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadAnalysis()
})
</script>

<style scoped>
.analysis-detail {
  padding: 24px;
}

.border {
  border: 1px solid rgba(0, 0, 0, 0.12);
}

.gap-2 {
  gap: 8px;
}
</style>
