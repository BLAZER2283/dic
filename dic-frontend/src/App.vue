<template>
  <v-app class="app">
    <AppNavigation v-if="showHeaderFooter" />

    <v-main>
      <router-view />
    </v-main>

    <AppFooter v-if="showHeaderFooter" />
  </v-app>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppNavigation from '@/components/AppNavigation.vue'
import AppFooter from '@/components/AppFooter.vue'

const route = useRoute()
const showHeaderFooter = computed(() =>
  !['module-select', 'login', 'register'].includes(route.name as string)
)
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');

:root {
  --text: #6b6375;
  --text-h: #08060d;
  --bg: #c4b8a5;
  --surface: #f0ebe0;
  --surface-border: #b8aa95;
  --accent: #2c2c2c;
  --accent-strong: #1a1a1a;
  --muted: #6b5e4a;
  --shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  min-height: 100%;
  background: var(--bg);
  color: var(--text);
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif;
}

body {
  background-color: var(--bg);
}

#app,
.v-application {
  min-height: 100vh;
  background: var(--bg) !important;
  color: var(--text);
}

.app {
  min-height: 100vh;
}

a {
  color: inherit;
  text-decoration: none;
}

h1, h2, h3, h4, h5, h6 {
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif;
  color: var(--text-h);
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem;
}

.grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

@media (min-width: 1024px) {
  .grid {
    grid-template-columns: 360px 1fr;
  }
}

.v-app-bar {
  background: var(--accent) !important;
  color: #e8e0d5 !important;
  border-bottom: 2px solid var(--accent-strong) !important;
  box-shadow: none !important;
}

.v-footer {
  background: var(--accent) !important;
  border-top: 2px solid var(--accent-strong) !important;
  color: #e8e0d5 !important;
}

.v-card,
.form-card,
.results-area,
.chart-card,
.warning-box,
.recommendations-box,
.kpi-card,
.v-sheet {
  background: var(--surface) !important;
  border: 1px solid var(--surface-border) !important;
  border-radius: 0 !important;
  box-shadow: none !important;
}

.v-card-title,
.form-title,
.chart-title,
.warning-title,
.recommendations-title {
  font-weight: 700;
  color: var(--text-h);
  font-size: 0.95rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid var(--surface-border);
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
}

label,
.field-label,
.summary,
.kpi-label,
.warning-title,
.recommendations-title {
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif;
}

label,
.field-label,
.summary {
  display: block;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-h);
  margin-bottom: 0.25rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

input,
select,
textarea,
.v-text-field input,
.v-text-field textarea {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--surface-border);
  border-radius: 0;
  font-size: 0.9375rem;
  background: #fffdf9;
  transition: none;
}

input:focus,
select:focus,
textarea:focus,
.v-text-field input:focus,
.v-select .v-field:focus {
  outline: none;
  border-color: var(--accent-strong);
  box-shadow: none;
}

.hint {
  font-size: 0.75rem;
  color: var(--muted);
  margin-top: 0.25rem;
  font-weight: 400;
}

.button-group,
.actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.5rem;
  flex-wrap: wrap;
}

.btn-primary,
.v-btn--variant-flat,
.v-btn--variant-flat:hover {
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif;
  text-transform: uppercase;
  letter-spacing: 1px;
  border-radius: 0 !important;
}

.btn-primary {
  background: var(--accent) !important;
  color: #f0ebe0 !important;
  padding: 0.75rem 1.25rem;
  border: none !important;
  font-size: 0.9375rem;
  font-weight: 700;
  cursor: pointer;
}

.btn-primary:hover {
  background: var(--accent-strong) !important;
}

.btn-secondary,
.v-btn--variant-outlined {
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif;
  text-transform: uppercase;
  letter-spacing: 1px;
  border-radius: 0 !important;
  background: #d4c9b8 !important;
  color: var(--accent) !important;
  border: 1px solid var(--surface-border) !important;
}

.btn-secondary:hover,
.v-btn--variant-outlined:hover {
  background: #c4b8a5 !important;
}

.v-btn--variant-flat {
  background: var(--accent) !important;
  color: #f0ebe0 !important;
}

.v-btn--variant-flat:hover {
  background: var(--accent-strong) !important;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

@media (min-width: 768px) {
  .kpi-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.kpi-card {
  padding: 1rem;
}

.kpi-label {
  font-size: 0.75rem;
  color: var(--muted);
  margin-bottom: 0.5rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.kpi-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--accent-strong);
}

.kpi-sub {
  font-size: 0.75rem;
  color: #8b7a62;
  margin-top: 0.25rem;
  font-weight: 400;
}

.warning-box,
.recommendations-box,
.chart-card {
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.warning-title,
.recommendations-title,
.chart-title {
  margin-bottom: 0.75rem;
}

.recommendations-list {
  list-style: none;
  padding-left: 0;
}

.recommendations-list li {
  font-size: 0.9rem;
  color: var(--text-h);
  margin-bottom: 0.5rem;
  display: flex;
  align-items: flex-start;
  font-weight: 400;
  line-height: 1.5;
}

.recommendations-list li::before {
  content: "■";
  color: var(--muted);
  font-weight: bold;
  margin-right: 0.5rem;
}

.text-green { color: #3d6b3d !important; }
.text-yellow { color: #9e7b3e !important; }
.text-red { color: #8b3a3a !important; }
.text-blue { color: #3a5c6b !important; }

.spinner {
  display: inline-block;
  width: 2rem;
  height: 2rem;
  border: 3px solid #d4c9b8;
  border-top-color: var(--accent);
  border-radius: 0px;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

::placeholder {
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif;
}
</style>
