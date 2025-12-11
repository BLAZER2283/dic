<template>
  <div id="app">
    <div style="padding: 20px; font-family: Arial, sans-serif;">
      <h1 style="color: #1976D2;">DIC Analyzer</h1>
      <p>Vue.js приложение загружено успешно!</p>

      <div style="margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
        <h2>Отладочная информация:</h2>
        <p><strong>Текущее время:</strong> {{ currentTime }}</p>
        <p><strong>Путь:</strong> {{ currentPath }}</p>
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

      <div style="margin: 20px 0;">
        <router-link to="/" style="margin-right: 10px; color: #1976D2;">Главная</router-link>
        <router-link to="/analyses" style="margin-right: 10px; color: #1976D2;">Анализы</router-link>
        <router-link to="/analyses/create" style="color: #1976D2;">Создать анализ</router-link>
      </div>

      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { version as vueVersion } from 'vue'

const route = useRoute()
const counter = ref(0)

const currentTime = computed(() => new Date().toLocaleString())
const currentPath = computed(() => route.path)

console.log('App component loaded')
console.log('Vue version:', vueVersion)

onMounted(() => {
  console.log('App component mounted')
  console.log('Current route:', route.path)
})
</script>

<style>
/* Global styles */
.v-application {
  font-family: 'Roboto', sans-serif;
}

.v-card {
  border-radius: 8px;
}

.v-btn {
  text-transform: none;
  letter-spacing: 0;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* Loading animation */
@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.loading-pulse {
  animation: pulse 1.5s ease-in-out infinite;
}
</style>
