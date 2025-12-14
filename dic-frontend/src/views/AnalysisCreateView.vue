<template>
  <div class="analysis-create">
    <!-- Header -->
    <v-row class="mb-6">
      <v-col cols="12">
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
            <h1 class="text-h4 font-weight-bold mb-2">Create New DIC Analysis</h1>
            <p class="text-body-1 text-grey-darken-1">
              Upload two images and configure parameters for digital image correlation analysis
            </p>
          </div>
        </div>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" lg="8">
        <v-card>
          <v-card-text class="pa-6">
            <v-form ref="form" v-model="valid">
              <!-- Analysis Name -->
              <v-text-field
                v-model="formData.name"
                label="Analysis Name"
                placeholder="Enter a descriptive name for your analysis"
                :rules="[rules.required]"
                class="mb-6"
              />

              <!-- Image Upload Section -->
              <div class="mb-6">
                <h3 class="text-h6 mb-4">Upload Images</h3>
                <p class="text-body-2 text-grey-darken-1 mb-4">
                  Upload the reference image (before deformation) and the deformed image (after deformation).
                  Supported formats: PNG, JPG, TIFF.
                </p>

                <v-row>
                  <!-- Before Image -->
                  <v-col cols="12" md="6">
                    <v-card
                      variant="outlined"
                      class="upload-card"
                      :class="{ 'upload-card--active': dragOver.before }"
                      @dragover.prevent="dragOver.before = true"
                      @dragleave.prevent="dragOver.before = false"
                      @drop.prevent="handleDrop('before', $event)"
                    >
                      <v-card-text class="text-center pa-6">
                        <v-icon
                          size="64"
                          color="grey-lighten-1"
                          class="mb-4"
                        >
                          mdi-image-outline
                        </v-icon>

                        <div v-if="!formData.image_before">
                          <div class="text-h6 mb-2">Reference Image</div>
                          <div class="text-body-2 text-grey-darken-1 mb-4">
                            Upload the image before deformation
                          </div>

                          <v-btn
                            color="primary"
                            variant="outlined"
                            @click="$refs.beforeInput.click()"
                            prepend-icon="mdi-upload"
                          >
                            Choose File
                          </v-btn>

                          <div class="mt-4 text-body-2 text-grey-darken-2">
                            or drag and drop here
                          </div>
                        </div>

                        <div v-else class="image-preview">
                          <div class="text-body-1 mb-2">{{ formData.image_before.name }}</div>
                          <v-img
                            :src="beforePreview"
                            max-height="200"
                            contain
                            class="mb-4 rounded"
                          />
                          <v-btn
                            size="small"
                            variant="text"
                            color="error"
                            @click="removeImage('before')"
                          >
                            Remove
                          </v-btn>
                        </div>

                        <input
                          ref="beforeInput"
                          type="file"
                          accept="image/*"
                          @change="handleFileSelect('before', $event)"
                          style="display: none"
                        />
                      </v-card-text>
                    </v-card>
                  </v-col>

                  <!-- After Image -->
                  <v-col cols="12" md="6">
                    <v-card
                      variant="outlined"
                      class="upload-card"
                      :class="{ 'upload-card--active': dragOver.after }"
                      @dragover.prevent="dragOver.after = true"
                      @dragleave.prevent="dragOver.after = false"
                      @drop.prevent="handleDrop('after', $event)"
                    >
                      <v-card-text class="text-center pa-6">
                        <v-icon
                          size="64"
                          color="grey-lighten-1"
                          class="mb-4"
                        >
                          mdi-image-outline
                        </v-icon>

                        <div v-if="!formData.image_after">
                          <div class="text-h6 mb-2">Deformed Image</div>
                          <div class="text-body-2 text-grey-darken-1 mb-4">
                            Upload the image after deformation
                          </div>

                          <v-btn
                            color="primary"
                            variant="outlined"
                            @click="$refs.afterInput.click()"
                            prepend-icon="mdi-upload"
                          >
                            Choose File
                          </v-btn>

                          <div class="mt-4 text-body-2 text-grey-darken-2">
                            or drag and drop here
                          </div>
                        </div>

                        <div v-else class="image-preview">
                          <div class="text-body-1 mb-2">{{ formData.image_after.name }}</div>
                          <v-img
                            :src="afterPreview"
                            max-height="200"
                            contain
                            class="mb-4 rounded"
                          />
                          <v-btn
                            size="small"
                            variant="text"
                            color="error"
                            @click="removeImage('after')"
                          >
                            Remove
                          </v-btn>
                        </div>

                        <input
                          ref="afterInput"
                          type="file"
                          accept="image/*"
                          @change="handleFileSelect('after', $event)"
                          style="display: none"
                        />
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
              </div>

              <!-- Sample Information Section -->
              <div class="mb-6">
                <h3 class="text-h6 mb-4">Sample Information</h3>
                <p class="text-body-2 text-grey-darken-1 mb-4">
                  Provide information about the sample being tested. This will be included in the analysis report.
                </p>

                <v-row>
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="formData.sample_name"
                      label="Sample Name"
                      placeholder="Enter sample name or identifier"
                      hint="Descriptive name for the tested sample"
                      persistent-hint
                    />
                  </v-col>

                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="formData.material"
                      label="Material"
                      placeholder="Enter material type"
                      hint="Material composition or type"
                      persistent-hint
                    />
                  </v-col>

                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="formData.manufacture"
                      label="Manufacturer"
                      placeholder="Enter manufacturer name"
                      hint="Company or entity that produced the sample"
                      persistent-hint
                    />
                  </v-col>

                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="formData.test_date"
                      label="Test Date"
                      type="date"
                      hint="Date when the test was performed"
                      persistent-hint
                    />
                  </v-col>
                </v-row>
              </div>

              <!-- Parameters Section -->
              <div class="mb-6">
                <h3 class="text-h6 mb-4">Analysis Parameters</h3>
                <p class="text-body-2 text-grey-darken-1 mb-4">
                  Configure the DIC algorithm parameters. Default values are recommended for most cases.
                </p>

                <v-row>
                  <v-col cols="12" md="4">
                    <v-text-field
                      v-model.number="formData.subset_size"
                      label="Subset Size"
                      type="number"
                      :rules="[rules.required, rules.subsetSize]"
                      hint="Size of correlation window (pixels)"
                      persistent-hint
                    />
                  </v-col>

                  <v-col cols="12" md="4">
                    <v-text-field
                      v-model.number="formData.step"
                      label="Step Size"
                      type="number"
                      :rules="[rules.required, rules.minValue(1)]"
                      hint="Step between correlation points"
                      persistent-hint
                    />
                  </v-col>

                  <v-col cols="12" md="4">
                    <v-text-field
                      v-model.number="formData.max_iter"
                      label="Max Iterations"
                      type="number"
                      :rules="[rules.required, rules.minValue(1)]"
                      hint="Maximum iterations for convergence"
                      persistent-hint
                    />
                  </v-col>

                  <v-col cols="12" md="4">
                    <v-text-field
                      v-model.number="formData.min_correlation"
                      label="Min Correlation"
                      type="number"
                      step="0.01"
                      :rules="[rules.required, rules.minValue(0), rules.maxValue(1)]"
                      hint="Minimum correlation coefficient"
                      persistent-hint
                    />
                  </v-col>
                </v-row>
              </div>

              <!-- Actions -->
              <div class="d-flex gap-4 justify-end">
                <v-btn
                  variant="text"
                  @click="$router.go(-1)"
                  :disabled="creating"
                >
                  Cancel
                </v-btn>
                <v-btn
                  color="primary"
                  size="large"
                  @click="() => { console.log('DEBUG: Button clicked'); submitForm(); }"
                  :loading="creating"
                  :disabled="!valid || !formData.image_before || !formData.image_after"
                >
                  Start Analysis
                </v-btn>
              </div>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Info Panel -->
      <v-col cols="12" lg="4">
        <v-card class="mb-4">
          <v-card-title>
            <v-icon left>mdi-information-outline</v-icon>
            DIC Analysis Info
          </v-card-title>
          <v-card-text>
            <div class="mb-4">
              <h4 class="text-body-1 font-weight-bold mb-2">What is DIC?</h4>
              <p class="text-body-2 text-grey-darken-1">
                Digital Image Correlation (DIC) is a non-contact optical method for measuring
                deformation and strain on surfaces. It compares two images to calculate displacement fields.
              </p>
            </div>

            <v-divider class="my-4"></v-divider>

            <div class="mb-4">
              <h4 class="text-body-1 font-weight-bold mb-2">Image Requirements</h4>
              <ul class="text-body-2 text-grey-darken-1">
                <li>Images should have similar lighting conditions</li>
                <li>Good contrast and texture on the surface</li>
                <li>Minimal out-of-plane deformation</li>
                <li>Same camera position and settings</li>
              </ul>
            </div>

            <v-divider class="my-4"></v-divider>

            <div>
              <h4 class="text-body-1 font-weight-bold mb-2">Parameters Guide</h4>
              <ul class="text-body-2 text-grey-darken-1">
                <li><strong>Subset Size:</strong> Larger values for noisy images</li>
                <li><strong>Step:</strong> Smaller values for higher resolution</li>
                <li><strong>Max Iterations:</strong> More iterations for convergence</li>
                <li><strong>Min Correlation:</strong> Lower values for poor images</li>
              </ul>
            </div>
          </v-card-text>
        </v-card>

        <!-- Processing Time Estimate -->
        <v-card v-if="formData.image_before && formData.image_after">
          <v-card-title>
            <v-icon left>mdi-timer-outline</v-icon>
            Estimated Processing Time
          </v-card-title>
          <v-card-text>
            <div class="text-h6 text-center mb-2">{{ estimatedTime }}</div>
            <div class="text-body-2 text-grey-darken-1 text-center">
              Based on image size and parameters
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Success Dialog -->
    <v-dialog v-model="showSuccessDialog" max-width="500">
      <v-card>
        <v-card-title class="text-h6 text-success">
          <v-icon left color="success">mdi-check-circle</v-icon>
          Analysis Created Successfully
        </v-card-title>
        <v-card-text>
          Your DIC analysis has been created and is now being processed.
          You can monitor its progress on the analyses page.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showSuccessDialog = false">
            Stay Here
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            @click="$router.push(`/analyses/${createdAnalysis?.id}`)"
          >
            View Analysis
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAnalysisStore } from '@/stores/analysis'
import type { DICAnalysis } from '@/types/api'

const router = useRouter()
const analysisStore = useAnalysisStore()

// Form data
const formData = reactive({
  name: '',
  image_before: null as File | null,
  image_after: null as File | null,
  subset_size: 25,
  step: 12,
  max_iter: 35,
  min_correlation: 0.4,
  // Sample information
  sample_name: '',
  material: '',
  manufacture: '',
  test_date: '',
})

// Form state
const valid = ref(false)
const creating = ref(false)
const showSuccessDialog = ref(false)
const createdAnalysis = ref<DICAnalysis | null>(null)

// Image previews
const beforePreview = ref<string>('')
const afterPreview = ref<string>('')
const dragOver = reactive({
  before: false,
  after: false,
})

// Form refs
const form = ref()
const beforeInput = ref<HTMLInputElement>()
const afterInput = ref<HTMLInputElement>()

// Validation rules
const rules = {
  required: (value: any) => !!value || 'This field is required',
  subsetSize: (value: number) => {
    if (value < 21 || value > 31) return 'Subset size must be between 21 and 31'
    if (value % 2 === 0) return 'Subset size must be odd'
    return true
  },
  minValue: (min: number) => (value: number) => value >= min || `Minimum value is ${min}`,
  maxValue: (max: number) => (value: number) => value <= max || `Maximum value is ${max}`,
}

// Computed
const debugValidation = computed(() => {
  const formValid = form.value?.validate() ?? false
  const hasImages = !!(formData.image_before && formData.image_after)
  const valid = valid.value
  console.log('DEBUG: Validation state:', { formValid, hasImages, valid })
  return { formValid, hasImages, valid }
})

const estimatedTime = computed(() => {
  // Simple estimation based on parameters
  const baseTime = 10 // seconds
  const sizeFactor = (formData.subset_size / 25) ** 2
  const iterFactor = formData.max_iter / 35
  const stepFactor = (12 / formData.step) ** 2

  const estimated = baseTime * sizeFactor * iterFactor * stepFactor
  return `${Math.round(estimated)}s - ${Math.round(estimated * 1.5)}s`
})

// Methods
const handleFileSelect = (type: 'before' | 'after', event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    setImage(type, file)
  }
}

const handleDrop = (type: 'before' | 'after', event: DragEvent) => {
  dragOver[type] = false
  const file = event.dataTransfer?.files?.[0]
  if (file && file.type.startsWith('image/')) {
    setImage(type, file)
  }
}

const setImage = (type: 'before' | 'after', file: File) => {
  if (type === 'before') {
    formData.image_before = file
    createPreview(file, 'before')
  } else {
    formData.image_after = file
    createPreview(file, 'after')
  }
}

const createPreview = (file: File, type: 'before' | 'after') => {
  const reader = new FileReader()
  reader.onload = (e) => {
    if (type === 'before') {
      beforePreview.value = e.target?.result as string
    } else {
      afterPreview.value = e.target?.result as string
    }
  }
  reader.readAsDataURL(file)
}

const removeImage = (type: 'before' | 'after') => {
  if (type === 'before') {
    formData.image_before = null
    beforePreview.value = ''
  } else {
    formData.image_after = null
    afterPreview.value = ''
  }
}

const submitForm = async () => {
  console.log('DEBUG: submitForm called')
  console.log('DEBUG: formData:', {
    name: formData.name,
    image_before: formData.image_before?.name,
    image_after: formData.image_after?.name,
    subset_size: formData.subset_size,
    step: formData.step,
    max_iter: formData.max_iter,
    min_correlation: formData.min_correlation,
    sample_name: formData.sample_name,
    material: formData.material,
    manufacture: formData.manufacture,
    test_date: formData.test_date
  })

  // Check if form exists
  console.log('DEBUG: form.value exists:', !!form.value)
  if (!form.value) {
    console.error('DEBUG: Form ref is null!')
    alert('Error: Form is not initialized')
    return
  }

  // Validate form
  console.log('DEBUG: Calling form.validate()')
  const isValid = form.value.validate()
  console.log('DEBUG: Form validation result:', isValid)

  // Check images
  console.log('DEBUG: image_before exists:', !!formData.image_before)
  console.log('DEBUG: image_after exists:', !!formData.image_after)

  if (!isValid || !formData.image_before || !formData.image_after) {
    console.log('DEBUG: Form validation failed or missing images - exiting')
    if (!isValid) {
      console.log('DEBUG: Form validation errors:', form.value.errors)
    }
    return
  }

  // Check if images are the same
  if (formData.image_before.name === formData.image_after.name) {
    console.log('DEBUG: Same image names detected')
    alert('Error: Please select different images for "before" and "after" states.')
    return
  }

  console.log('DEBUG: All validation passed, starting analysis creation')
  creating.value = true
  try {
    console.log('DEBUG: Calling analysisStore.createAnalysis')
    const analysis = await analysisStore.createAnalysis(formData)
    console.log('DEBUG: Analysis created successfully:', analysis)
    createdAnalysis.value = analysis
    showSuccessDialog.value = true

    // Reset form
    formData.name = ''
    formData.image_before = null
    formData.image_after = null
    beforePreview.value = ''
    afterPreview.value = ''
    form.value?.resetValidation()
  } catch (error) {
    console.error('DEBUG: Failed to create analysis:', error)
    // Show error message to user
    const errorMessage = error.response?.data?.detail ||
                        error.response?.data?.error ||
                        error.response?.data ||
                        error.message ||
                        'Failed to create analysis'
    console.error('DEBUG: Error details:', {
      response: error.response,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message
    })
    alert(`Error: ${JSON.stringify(errorMessage)}`)
  } finally {
    creating.value = false
  }
}

// Initialize with current date in name
onMounted(() => {
  const now = new Date()
  formData.name = `DIC Analysis ${now.toLocaleDateString()} ${now.toLocaleTimeString()}`
})
</script>

<style scoped>
.analysis-create {
  padding: 24px;
}

.upload-card {
  border: 2px dashed rgb(var(--v-theme-grey-lighten-1));
  transition: all 0.3s ease;
  cursor: pointer;
  min-height: 300px;
  display: flex;
  align-items: center;
}

.upload-card:hover {
  border-color: rgb(var(--v-theme-primary));
  background-color: rgba(var(--v-theme-primary), 0.04);
}

.upload-card--active {
  border-color: rgb(var(--v-theme-primary));
  background-color: rgba(var(--v-theme-primary), 0.08);
}

.image-preview {
  width: 100%;
}

.gap-4 {
  gap: 16px;
}
</style>
