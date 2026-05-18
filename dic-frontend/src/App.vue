<template>
  <v-app>
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

.v-application {
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif !important;
  background: #c4b8a5 !important;
}

.v-card {
  background: #f0ebe0 !important;
  border: 1px solid #b8aa95 !important;
  border-radius: 0 !important;
}

.v-card-title {
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif;
  font-weight: 700;
  color: #2c2c2c;
  font-size: 0.95rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #b8aa95;
  padding-bottom: 0.5rem;
}

.v-card-text {
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif;
  color: #2c2c2c;
}

.v-btn {
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif;
  text-transform: uppercase;
  letter-spacing: 1px;
  border-radius: 0 !important;
}

.v-btn--variant-outlined {
  border: 1px solid #b8aa95 !important;
  color: #2c2c2c !important;
  background: #d4c9b8 !important;
}

.v-btn--variant-outlined:hover {
  background: #c4b8a5 !important;
}

.v-btn--variant-flat {
  background: #2c2c2c !important;
  color: #f0ebe0 !important;
}

.v-btn--variant-flat:hover {
  background: #1a1a1a !important;
}

.v-text-field input,
.v-text-field textarea {
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif;
  background: #fffdf9;
}

.v-select .v-field {
  background: #fffdf9;
  border-radius: 0;
}

.v-field__input {
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif;
}

.v-chip {
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif;
  border-radius: 0 !important;
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
