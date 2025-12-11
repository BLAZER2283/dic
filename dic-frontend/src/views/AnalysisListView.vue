<template>
  <div class="analysis-list">
    <!-- Header -->
    <v-row class="mb-6">
      <v-col cols="12">
        <div class="d-flex align-center justify-space-between flex-wrap">
          <div>
            <h1 class="text-h4 font-weight-bold mb-2">DIC Analyses</h1>
            <p class="text-body-1 text-grey-darken-1">
              Manage and monitor your digital image correlation analyses
            </p>
          </div>
          <div class="d-flex gap-2 flex-wrap">
            <v-btn
              color="primary"
              @click="$router.push('/analyses/create')"
              prepend-icon="mdi-plus"
            >
              New Analysis
            </v-btn>
            <v-btn
              variant="outlined"
              @click="refreshData"
              prepend-icon="mdi-refresh"
              :loading="loading"
            >
              Refresh
            </v-btn>
          </div>
        </div>
      </v-col>
    </v-row>

    <!-- Filters -->
    <v-row class="mb-6">
      <v-col cols="12">
        <v-card>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="3">
                <v-text-field
                  v-model="searchQuery"
                  label="Search"
                  prepend-inner-icon="mdi-magnify"
                  clearable
                  hide-details
                  @input="debouncedSearch"
                />
              </v-col>

              <v-col cols="12" md="2">
                <v-select
                  v-model="statusFilter"
                  :items="statusOptions"
                  label="Status"
                  clearable
                  hide-details
                />
              </v-col>

              <v-col cols="12" md="2">
                <v-select
                  v-model="hasResultsFilter"
                  :items="resultsOptions"
                  label="Results"
                  clearable
                  hide-details
                />
              </v-col>

              <v-col cols="12" md="2">
                <v-text-field
                  v-model="dateFrom"
                  label="From Date"
                  type="date"
                  hide-details
                />
              </v-col>

              <v-col cols="12" md="2">
                <v-text-field
                  v-model="dateTo"
                  label="To Date"
                  type="date"
                  hide-details
                />
              </v-col>

              <v-col cols="12" md="1" class="d-flex align-end">
                <v-btn
                  variant="text"
                  @click="clearFilters"
                  color="grey-darken-1"
                  size="small"
                >
                  Clear
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Bulk Actions -->
    <v-row v-if="selected.length > 0" class="mb-4">
      <v-col cols="12">
        <v-card color="grey-lighten-4">
          <v-card-text class="d-flex align-center justify-space-between">
            <span class="text-body-1">
              {{ selected.length }} analysis{{ selected.length > 1 ? 'es' : '' }} selected
            </span>
            <div class="d-flex gap-2">
              <v-btn
                color="error"
                variant="outlined"
                size="small"
                @click="confirmBulkDelete"
                prepend-icon="mdi-delete"
              >
                Delete Selected
              </v-btn>
              <v-btn
                variant="text"
                size="small"
                @click="selected = []"
              >
                Clear Selection
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Data Table -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-text class="pa-0">
            <v-data-table
              v-model="selected"
              :headers="headers"
              :items="analyses"
              :loading="loading"
              item-key="id"
              show-select
              :items-per-page="pageSize"
              :page="currentPage"
              :server-items-length="totalCount"
              :disable-pagination="loading"
              density="comfortable"
              @update:options="handlePagination"
              @click:row="(item) => $router.push(`/analyses/${item.id}`)"
              class="cursor-pointer"
            >
              <template #[`item.status`]="{ item }">
                <v-chip
                  :color="getStatusColor(item.status)"
                  size="small"
                  variant="flat"
                >
                  {{ item.status_display }}
                </v-chip>
              </template>

              <template #[`item.created_at`]="{ item }">
                <div class="text-caption">
                  {{ formatDate(item.created_at) }}
                </div>
              </template>

              <template #[`item.processing_time`]="{ item }">
                <div v-if="item.processing_time" class="text-caption">
                  {{ item.processing_time.toFixed(1) }}s
                </div>
                <div v-else class="text-caption text-grey-darken-1">-</div>
              </template>

              <template #[`item.max_displacement`]="{ item }">
                <div v-if="item.max_displacement !== null" class="text-caption">
                  {{ item.max_displacement.toFixed(4) }}
                </div>
                <div v-else class="text-caption text-grey-darken-1">-</div>
              </template>

              <template #[`item.actions`]="{ item }">
                <v-menu>
                  <template #activator="{ props }">
                    <v-btn
                      variant="text"
                      size="small"
                      v-bind="props"
                      @click.stop
                    >
                      <v-icon>mdi-dots-vertical</v-icon>
                    </v-btn>
                  </template>

                  <v-list density="compact">
                    <v-list-item @click="$router.push(`/analyses/${item.id}`)">
                      <v-list-item-icon>
                        <v-icon>mdi-eye</v-icon>
                      </v-list-item-icon>
                      <v-list-item-title>View Details</v-list-item-title>
                    </v-list-item>

                    <v-list-item
                      v-if="item.status === 'completed'"
                      @click="downloadResults(item.id)"
                    >
                      <v-list-item-icon>
                        <v-icon>mdi-download</v-icon>
                      </v-list-item-icon>
                      <v-list-item-title>Download Results</v-list-item-title>
                    </v-list-item>

                    <v-list-item
                      v-if="item.status === 'processing' || item.status === 'pending'"
                      @click="cancelAnalysis(item.id)"
                    >
                      <v-list-item-icon>
                        <v-icon color="error">mdi-cancel</v-icon>
                      </v-list-item-icon>
                      <v-list-item-title>Cancel</v-list-item-title>
                    </v-list-item>
                  </v-list>
                </v-menu>
              </template>

              <template #bottom>
                <div class="d-flex align-center justify-space-between pa-4">
                  <div class="text-body-2 text-grey-darken-1">
                    Showing {{ startItem }}-{{ endItem }} of {{ totalCount }} analyses
                  </div>
                  <v-pagination
                    v-model="currentPage"
                    :length="totalPages"
                    :total-visible="7"
                    @update:model-value="goToPage"
                  />
                </div>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Bulk Delete Confirmation Dialog -->
    <v-dialog v-model="showBulkDeleteDialog" max-width="500">
      <v-card>
        <v-card-title class="text-h6">
          Confirm Bulk Delete
        </v-card-title>
        <v-card-text>
          Are you sure you want to delete {{ selected.length }} analysis{{ selected.length > 1 ? 'es' : '' }}?
          This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showBulkDeleteDialog = false">
            Cancel
          </v-btn>
          <v-btn
            color="error"
            variant="flat"
            @click="executeBulkDelete"
            :loading="bulkDeleting"
          >
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useAnalysisStore } from '@/stores/analysis'
import type { DICAnalysis } from '@/types/api'

const analysisStore = useAnalysisStore()

// Reactive data
const selected = ref<DICAnalysis[]>([])
const showBulkDeleteDialog = ref(false)
const bulkDeleting = ref(false)
const searchTimeout = ref<NodeJS.Timeout | null>(null)

// Computed
const analyses = computed(() => analysisStore.analyses)
const loading = computed(() => analysisStore.loading)
const currentPage = computed(() => analysisStore.currentPage)
const pageSize = computed(() => analysisStore.pageSize)
const totalCount = computed(() => analysisStore.totalCount)
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))

const startItem = computed(() => (currentPage.value - 1) * pageSize.value + 1)
const endItem = computed(() => Math.min(currentPage.value * pageSize.value, totalCount.value))

const searchQuery = computed({
  get: () => analysisStore.searchQuery,
  set: (value) => analysisStore.setSearchQuery(value)
})

const statusFilter = computed({
  get: () => analysisStore.statusFilter,
  set: (value) => analysisStore.setStatusFilter(value)
})

const hasResultsFilter = computed({
  get: () => analysisStore.hasResultsFilter,
  set: (value) => analysisStore.setHasResultsFilter(value)
})

const dateFrom = computed({
  get: () => analysisStore.dateFrom,
  set: (value) => {
    analysisStore.dateFrom = value
    if (value && analysisStore.dateTo) {
      analysisStore.setDateRange(value, analysisStore.dateTo)
    }
  }
})

const dateTo = computed({
  get: () => analysisStore.dateTo,
  set: (value) => {
    analysisStore.dateTo = value
    if (value && analysisStore.dateFrom) {
      analysisStore.setDateRange(analysisStore.dateFrom, value)
    }
  }
})

// Data table headers
const headers = [
  { title: 'Name', key: 'name', width: '25%' },
  { title: 'Status', key: 'status', width: '15%', sortable: false },
  { title: 'Created', key: 'created_at', width: '20%', sortable: true },
  { title: 'Processing Time', key: 'processing_time', width: '15%', sortable: true },
  { title: 'Max Displacement', key: 'max_displacement', width: '15%', sortable: true },
  { title: 'Actions', key: 'actions', width: '10%', sortable: false },
]

// Options for filters
const statusOptions = [
  { title: 'Pending', value: 'pending' },
  { title: 'Processing', value: 'processing' },
  { title: 'Completed', value: 'completed' },
  { title: 'Error', value: 'error' },
  { title: 'Cancelled', value: 'cancelled' },
]

const resultsOptions = [
  { title: 'Has Results', value: true },
  { title: 'No Results', value: false },
]

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

const debouncedSearch = () => {
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }
  searchTimeout.value = setTimeout(() => {
    analysisStore.fetchAnalyses(1)
  }, 500)
}

const refreshData = () => {
  analysisStore.fetchAnalyses(currentPage.value)
}

const handlePagination = (options: any) => {
  if (options.page !== currentPage.value) {
    analysisStore.goToPage(options.page)
  }
}

const goToPage = (page: number) => {
  analysisStore.goToPage(page)
}

const clearFilters = () => {
  analysisStore.clearFilters()
  selected.value = []
}

const cancelAnalysis = async (id: string) => {
  try {
    await analysisStore.cancelAnalysis(id)
  } catch (error) {
    console.error('Failed to cancel analysis:', error)
  }
}

const downloadResults = async (id: string) => {
  try {
    await analysisStore.downloadResults(id)
  } catch (error) {
    console.error('Failed to download results:', error)
  }
}

const confirmBulkDelete = () => {
  showBulkDeleteDialog.value = true
}

const executeBulkDelete = async () => {
  bulkDeleting.value = true
  try {
    const ids = selected.value.map(item => item.id)
    await analysisStore.bulkDeleteAnalyses(ids)
    selected.value = []
    showBulkDeleteDialog.value = false
  } catch (error) {
    console.error('Failed to delete analyses:', error)
  } finally {
    bulkDeleting.value = false
  }
}

// Lifecycle
onMounted(() => {
  analysisStore.fetchAnalyses()
})

// Watch for filter changes
watch([statusFilter, hasResultsFilter], () => {
  analysisStore.fetchAnalyses(1)
  selected.value = []
})
</script>

<style scoped>
.analysis-list {
  padding: 24px;
}

.cursor-pointer {
  cursor: pointer;
}

.cursor-pointer:hover {
  background-color: rgba(0, 0, 0, 0.04);
}

.gap-2 {
  gap: 8px;
}
</style>
