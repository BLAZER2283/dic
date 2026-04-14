import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

import { useAuthStore } from './auth/stores/auth.store'
import { setupAuthGuard } from './auth/plugin'

import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'light'
  }
})

const app = createApp(App)

const pinia = createPinia()
app.use(pinia)
app.use(vuetify)

// Инициализация auth ДО установки роутера
const authStore = useAuthStore()

authStore.initAuth().then(() => {
  // Установка guard для защищенных маршрутов
  setupAuthGuard(router)
  app.use(router)
  app.mount('#app')
})
