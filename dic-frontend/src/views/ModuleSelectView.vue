<template>
  <v-container class="module-select-container" fluid>
    <div class="module-select-wrapper">
      <div class="header">
        <h1>DIC & UCRP</h1>
        <p>Выберите модуль для работы</p>
      </div>

      <div class="modules-grid">
        <router-link to="/" class="module-card module-card--dic">
          <div class="module-icon">
            <v-icon size="64" color="#2c2c2c">mdi-image-multiple-outline</v-icon>
          </div>
          <h2>DIC Analyzer</h2>
          <p>Цифровая корреляция изображений. Анализ деформаций и перемещений.</p>
          <span class="module-btn">Перейти</span>
        </router-link>

        <a href="/ucrp/" class="module-card module-card--ucrp">
          <div class="module-icon">
            <v-icon size="64" color="#2c2c2c">mdi-robot</v-icon>
          </div>
          <h2>Plasma Optimizer</h2>
          <p>UCRP — оптимизация параметров плазменной обработки материалов.</p>
          <span class="module-btn">Перейти</span>
        </a>
      </div>
    </div>
  </v-container>
</template>

<script setup lang="ts">
</script>

<style scoped>
.module-select-container {
  min-height: calc(100vh - 64px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: #c4b8a5;
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif;
}

.module-select-wrapper {
  width: 100%;
  max-width: 800px;
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 2px solid #b8aa95;
}

.header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #2c2c2c;
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 8px;
}

.header p {
  font-size: 1rem;
  color: #6b5e4a;
}

.modules-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.module-card {
  background: #f0ebe0;
  border: 2px solid #b8aa95;
  padding: 40px 32px;
  text-align: center;
  text-decoration: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.module-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12);
  border-color: #2c2c2c;
}

.module-icon {
  margin-bottom: 20px;
}

.module-card h2 {
  font-size: 1.3rem;
  font-weight: 700;
  color: #2c2c2c;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 12px;
}

.module-card p {
  font-size: 0.85rem;
  color: #6b5e4a;
  line-height: 1.5;
  margin-bottom: 24px;
}

.module-btn {
  display: inline-block;
  padding: 12px 32px;
  background: #2c2c2c;
  color: #f0ebe0;
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  transition: background 0.2s ease;
}

.module-card:hover .module-btn {
  background: #1a1a1a;
}
</style>
