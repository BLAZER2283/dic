<template>
  <div class="analysis-create">
    <div class="create-header">
      <h1>Создание нового анализа</h1>
      <p>Загрузите два изображения и настройте параметры для анализа DIC</p>
    </div>

    <v-row>
      <v-col cols="12" lg="8">
        <v-card>
          <v-card-title class="section-title">
            <v-icon left class="section-icon">mdi-image-outline</v-icon>
            Загрузка изображений
          </v-card-title>
          <v-card-text class="pa-6">
            <v-form ref="form" v-model="valid">
              <div class="form-group">
                <label>Название анализа</label>
                <v-text-field
                  v-model="formData.name"
                  placeholder="Введите название"
                  variant="outlined"
                  density="compact"
                  hide-details
                  :rules="[rules.required]"
                  class="mb-4"
                />
              </div>

              <v-row>
                <v-col cols="12" md="6">
                  <div class="upload-card" :class="{ 'upload-card--active': dragOver.before }"
                    @dragover.prevent="dragOver.before = true"
                    @dragleave.prevent="dragOver.before = false"
                    @drop.prevent="handleDrop('before', $event)">
                    <div v-if="!formData.image_before">
                      <div class="upload-icon">📷</div>
                      <div class="upload-title">Эталонное изображение</div>
                      <div class="upload-subtitle">До деформации</div>
                      <v-btn
                        variant="outlined"
                        @click="$refs.beforeInput.click()"
                        class="btn-upload"
                      >
                        Выбрать файл
                      </v-btn>
                      <div class="upload-hint">или перетащите сюда</div>
                    </div>
                    <div v-else class="image-preview">
                      <v-img :src="beforePreview" max-height="200" contain class="mb-4" />
                      <div class="file-name">{{ formData.image_before.name }}</div>
                      <v-btn size="small" variant="outlined" color="error" @click="removeImage('before')">
                        Удалить
                      </v-btn>
                    </div>
                    <input ref="beforeInput" type="file" accept="image/*" @change="handleFileSelect('before', $event)" style="display: none" />
                  </div>
                </v-col>

                <v-col cols="12" md="6">
                  <div class="upload-card" :class="{ 'upload-card--active': dragOver.after }"
                    @dragover.prevent="dragOver.after = true"
                    @dragleave.prevent="dragOver.after = false"
                    @drop.prevent="handleDrop('after', $event)">
                    <div v-if="!formData.image_after">
                      <div class="upload-icon">📷</div>
                      <div class="upload-title">Деформированное изображение</div>
                      <div class="upload-subtitle">После деформации</div>
                      <v-btn
                        variant="outlined"
                        @click="$refs.afterInput.click()"
                        class="btn-upload"
                      >
                        Выбрать файл
                      </v-btn>
                      <div class="upload-hint">или перетащите сюда</div>
                    </div>
                    <div v-else class="image-preview">
                      <v-img :src="afterPreview" max-height="200" contain class="mb-4" />
                      <div class="file-name">{{ formData.image_after.name }}</div>
                      <v-btn size="small" variant="outlined" color="error" @click="removeImage('after')">
                        Удалить
                      </v-btn>
                    </div>
                    <input ref="afterInput" type="file" accept="image/*" @change="handleFileSelect('after', $event)" style="display: none" />
                  </div>
                </v-col>
              </v-row>

              <div class="section-divider"></div>

              <div class="form-section">
                <div class="section-title-sm">Информация о образце</div>
                <v-row>
                  <v-col cols="12" md="6">
                    <label class="field-label">Название</label>
                    <v-text-field v-model="formData.sample_name" placeholder="Название образца" variant="outlined" density="compact" hide-details />
                  </v-col>
                  <v-col cols="12" md="6">
                    <label class="field-label">Материал</label>
                    <v-text-field v-model="formData.material" placeholder="Материал" variant="outlined" density="compact" hide-details />
                  </v-col>
                  <v-col cols="12" md="6">
                    <label class="field-label">Производитель</label>
                    <v-text-field v-model="formData.manufacture" placeholder="Производитель" variant="outlined" density="compact" hide-details />
                  </v-col>
                  <v-col cols="12" md="6">
                    <label class="field-label">Дата испытания</label>
                    <v-text-field v-model="formData.test_date" type="date" variant="outlined" density="compact" hide-details />
                  </v-col>
                </v-row>
              </div>

              <div class="section-divider"></div>

              <div class="form-section">
                <div class="section-title-sm">Параметры анализа</div>
                <v-row>
                  <v-col cols="12" md="4">
                    <label class="field-label">Размер подмножества</label>
                    <v-text-field v-model.number="formData.subset_size" type="number" variant="outlined" density="compact" hide-details :rules="[rules.subsetSize]" />
                  </v-col>
                  <v-col cols="12" md="4">
                    <label class="field-label">Шаг</label>
                    <v-text-field v-model.number="formData.step" type="number" variant="outlined" density="compact" hide-details />
                  </v-col>
                  <v-col cols="12" md="4">
                    <label class="field-label">Макс. итераций</label>
                    <v-text-field v-model.number="formData.max_iter" type="number" variant="outlined" density="compact" hide-details />
                  </v-col>
                  <v-col cols="12" md="4">
                    <label class="field-label">Мин. корреляция</label>
                    <v-text-field v-model.number="formData.min_correlation" type="number" step="0.01" variant="outlined" density="compact" hide-details />
                  </v-col>
                </v-row>
              </div>

              <div class="form-actions">
                <v-btn variant="outlined" @click="$router.go(-1)" :disabled="creating" class="btn-secondary">
                  Отмена
                </v-btn>
                <v-btn
                  color="primary"
                  @click="submitForm"
                  :loading="creating"
                  :disabled="!valid || !formData.image_before || !formData.image_after"
                  class="btn-primary"
                >
                  Начать анализ
                </v-btn>
              </div>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" lg="4">
        <v-card class="info-card">
          <v-card-title class="section-title">
            <v-icon left class="section-icon">mdi-information-outline</v-icon>
            О DIC анализе
          </v-card-title>
          <v-card-text>
            <div class="info-text">
              <strong>Что такое DIC?</strong>
              <p>Цифровая корреляция изображений (DIC) — бесконтактный оптический метод измерения деформаций и напряжений на поверхности.</p>
            </div>
            <div class="info-divider"></div>
            <div class="info-text">
              <strong>Требования к изображениям:</strong>
              <ul>
                <li>Одинаковые условия освещения</li>
                <li>Хороший контраст и текстура</li>
                <li>Минимальная деформация</li>
              </ul>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
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
  correlationValue: (value: number) => {
    if (value === undefined || value === null) return 'Required'
    if (value < 0 || value > 1) return 'Must be between 0 and 1'
    return true
  },
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
  console.log('DEBUG: min_correlation value being sent:', formData.min_correlation)
  creating.value = true
  try {
    console.log('DEBUG: Calling analysisStore.createAnalysis')
    const analysis = await analysisStore.createAnalysis(formData)
    console.log('DEBUG: Analysis created successfully:', analysis)
    console.log('DEBUG: Analysis min_correlation from server:', analysis.min_correlation)
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
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif;
  background: #c4b8a5;
  min-height: 100vh;
}

.create-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #b8aa95;
}

.create-header h1 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #2c2c2c;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 8px;
}

.create-header p {
  font-size: 0.85rem;
  color: #6b5e4a;
}

.v-card {
  background: #f0ebe0 !important;
  border: 1px solid #b8aa95 !important;
  border-radius: 0 !important;
}

.section-title {
  font-size: 0.85rem !important;
  font-weight: 700 !important;
  color: #2c2c2c !important;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #b8aa95;
  padding-bottom: 8px;
}

.section-icon {
  font-size: 18px !important;
  margin-right: 8px;
}

.section-title-sm {
  font-size: 0.75rem;
  font-weight: 700;
  color: #2c2c2c;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 16px;
}

.upload-card {
  background: #fffdf9;
  border: 2px dashed #b8aa95;
  padding: 32px 16px;
  text-align: center;
  min-height: 280px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: none;
}

.upload-card:hover {
  border-color: #2c2c2c;
  background: #f5f0e5;
}

.upload-card--active {
  border-color: #2c2c2c;
  background: #e8e0d5;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.upload-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #2c2c2c;
  margin-bottom: 4px;
}

.upload-subtitle {
  font-size: 0.75rem;
  color: #6b5e4a;
  margin-bottom: 16px;
}

.btn-upload {
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif !important;
  font-size: 0.75rem !important;
  text-transform: uppercase;
  letter-spacing: 1px;
  border: 1px solid #b8aa95 !important;
  background: #d4c9b8 !important;
  color: #2c2c2c !important;
}

.upload-hint {
  font-size: 0.7rem;
  color: #8b7a62;
  margin-top: 12px;
}

.image-preview {
  width: 100%;
}

.file-name {
  font-size: 0.75rem;
  color: #2c2c2c;
  margin-bottom: 12px;
  word-break: break-all;
}

.section-divider {
  height: 2px;
  background: #b8aa95;
  margin: 24px 0;
}

.form-section {
  margin-bottom: 16px;
}

.field-label {
  display: block;
  font-size: 0.7rem;
  font-weight: 700;
  color: #6b5e4a;
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  justify-content: flex-end;
}

.btn-primary {
  background: #2c2c2c !important;
  color: #f0ebe0 !important;
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif !important;
  font-size: 0.8rem !important;
  text-transform: uppercase;
  letter-spacing: 1px;
  border-radius: 0 !important;
}

.btn-secondary {
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif !important;
  font-size: 0.8rem !important;
  text-transform: uppercase;
  letter-spacing: 1px;
  border: 1px solid #b8aa95 !important;
  background: #d4c9b8 !important;
  color: #2c2c2c !important;
  border-radius: 0 !important;
}

.info-card {
  background: #f0ebe0 !important;
  border: 1px solid #b8aa95 !important;
}

.info-text {
  font-size: 0.85rem;
  color: #2c2c2c;
  line-height: 1.5;
}

.info-text strong {
  font-weight: 700;
}

.info-text ul {
  padding-left: 16px;
  margin-top: 8px;
}

.info-text li {
  margin-bottom: 4px;
}

.info-divider {
  height: 1px;
  background: #b8aa95;
  margin: 16px 0;
}
</style>
