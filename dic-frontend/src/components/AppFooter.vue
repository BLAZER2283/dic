<template>
  <v-footer app class="footer">
    <v-container>
      <v-row justify="center" align="center">
        <v-col cols="12" md="6" class="text-center text-md-left">
          <div class="d-flex align-center justify-center justify-md-start">
            <span class="footer-text">
              DIC Analyzer — Digital Image Correlation Analysis Tool
            </span>
          </div>
        </v-col>

        <v-col cols="12" md="6" class="text-center text-md-right">
          <span class="footer-sub">
            © {{ currentYear }} — Автоматизация расчёта параметров УЦР
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
.footer {
  background: #2c2c2c !important;
  border-top: 2px solid #1a1a1a !important;
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif;
}

.footer-text {
  font-size: 0.8rem;
  font-weight: 600;
  color: #e8e0d5;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.footer-sub {
  font-size: 0.7rem;
  color: #8b7a62;
  font-weight: 400;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
</style>
