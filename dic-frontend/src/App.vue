<template>
  <v-app class="app">
    <AppNavigation />

    <v-main>
      <router-view />
    </v-main>

    <AppFooter />
  </v-app>
</template>

<script setup lang="ts">
import AppNavigation from '@/components/AppNavigation.vue'
import AppFooter from '@/components/AppFooter.vue'
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif;
  background: #c4b8a5;
}

#app,
.v-application {
  min-height: 100vh;
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif !important;
  background: #c4b8a5 !important;
}

.app {
  min-height: 100vh;
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

.v-card,
.form-card,
.results-area,
.chart-card,
.warning-box,
.recommendations-box,
.kpi-card {
  background: #f0ebe0 !important;
  border: 1px solid #b8aa95 !important;
  border-radius: 0 !important;
  box-shadow: none !important;
}

.form-title,
.chart-title,
.warning-title,
.recommendations-title,
.v-card-title {
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif;
  font-weight: 700;
  color: #2c2c2c;
  font-size: 0.95rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #b8aa95;
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
  color: #2c2c2c;
  margin-bottom: 0.25rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

input,
select,
.v-text-field input,
.v-text-field textarea {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #b8aa95;
  border-radius: 0;
  font-size: 0.9375rem;
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif;
  background: #fffdf9;
  transition: none;
}

input:focus,
select:focus,
.v-text-field input:focus,
.v-select .v-field:focus {
  outline: none;
  border-color: #2c2c2c;
  box-shadow: none;
}

.hint {
  font-size: 0.75rem;
  color: #6b5e4a;
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
  background: #2c2c2c;
  color: #f0ebe0;
  padding: 0.625rem 1rem;
  border: none;
  font-size: 0.9375rem;
  font-weight: 700;
  cursor: pointer;
}

.btn-primary:hover {
  background: #1a1a1a;
}

.btn-secondary,
.v-btn--variant-outlined {
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif;
  text-transform: uppercase;
  letter-spacing: 1px;
  border-radius: 0 !important;
  background: #d4c9b8 !important;
  color: #2c2c2c !important;
  border: 1px solid #b8aa95 !important;
}

.btn-secondary:hover,
.v-btn--variant-outlined:hover {
  background: #c4c5a5 !important;
}

.v-btn--variant-flat {
  background: #2c2c2c !important;
  color: #f0ebe0 !important;
}

.v-btn--variant-flat:hover {
  background: #1a1a1a !important;
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
  color: #6b5e4a;
  margin-bottom: 0.5rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.kpi-value {
  font-size: 1.4375rem;
  font-weight: 700;
  color: #2c2c2c;
}

.kpi-sub {
  font-size: 0.7rem;
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
  font-size: 0.85rem;
  color: #2c2c2c;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: flex-start;
  font-weight: 400;
  line-height: 1.4;
}

.recommendations-list li::before {
  content: "■";
  color: #6b5e4a;
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
  border-top-color: #2c2c2c;
  border-radius: 0px;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #d4c9b8;
}

::-webkit-scrollbar-thumb {
  background: #b8aa95;
}

::placeholder {
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif;
}
</style>
