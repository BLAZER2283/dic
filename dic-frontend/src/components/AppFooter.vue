<template>
  <v-footer app color="grey lighten-4" class="mt-8">
    <v-container>
      <v-row justify="center" align="center">
        <v-col cols="12" md="6" class="text-center text-md-left">
          <div class="d-flex align-center justify-center justify-md-start">
            <v-icon color="primary" class="me-2">mdi-chart-line</v-icon>
            <span class="text-body-2">
              DIC Analyzer - Digital Image Correlation Analysis Tool
            </span>
          </div>
        </v-col>

        <v-col cols="12" md="6" class="text-center text-md-right">
          <span class="text-caption text-grey-darken-1">
            © {{ currentYear }} DIC Analyzer. Built with Vue.js & Django.
          </span>
        </v-col>
      </v-row>
    </v-container>
  </v-footer>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const currentYear = computed(() => new Date().getFullYear())
</script>

<style scoped>
.v-footer {
  border-top: 1px solid rgba(0, 0, 0, 0.12);
}
</style>
