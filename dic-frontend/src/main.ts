import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from './views/DashboardView.vue'

console.log('Starting Vue app...')

try {
  const app = createApp({
    template: `
      <div id="app">
        <div style="padding: 20px; font-family: Arial, sans-serif;">
          <h1 style="color: #1976D2;">DIC Analyzer</h1>
          <p>Vue.js приложение загружено успешно!</p>

          <div style="margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
            <h2>Отладочная информация:</h2>
            <p><strong>Текущее время:</strong> {{ currentTime }}</p>
            <p><strong>Vue версия:</strong> {{ vueVersion }}</p>
          </div>

          <div style="margin: 20px 0;">
            <button
              @click="counter++"
              style="padding: 10px 20px; background: #1976D2; color: white; border: none; border-radius: 4px; cursor: pointer;"
            >
              Счетчик: {{ counter }}
            </button>
          </div>

          <DashboardView />
        </div>
      </div>
    `,
    data() {
      return {
        counter: 0,
        currentTime: new Date().toLocaleString(),
        vueVersion: '3.x'
      }
    },
    components: {
      DashboardView
    },
    mounted() {
      console.log('App component mounted')
      setInterval(() => {
        this.currentTime = new Date().toLocaleString()
      }, 1000)
    }
  })

  console.log('App created')

  app.mount('#app')
  console.log('App mounted successfully!')
} catch (error) {
  console.error('Error initializing Vue app:', error)
}
