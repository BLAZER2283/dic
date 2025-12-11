<template>
  <v-app-bar app color="primary" dark elevation="2">
    <v-app-bar-nav-icon @click="drawer = !drawer" class="d-md-none" />

    <v-toolbar-title class="d-flex align-center">
      <v-icon class="me-2">mdi-chart-line</v-icon>
      DIC Analyzer
    </v-toolbar-title>

    <v-spacer />

    <v-btn
      v-if="$route.name !== 'dashboard'"
      variant="text"
      @click="$router.push('/')"
      class="d-none d-md-flex"
    >
      <v-icon left>mdi-view-dashboard</v-icon>
      Dashboard
    </v-btn>

    <v-btn
      v-if="$route.name !== 'analysis-list'"
      variant="text"
      @click="$router.push('/analyses')"
      class="d-none d-md-flex"
    >
      <v-icon left>mdi-format-list-bulleted</v-icon>
      Analyses
    </v-btn>

    <v-btn
      variant="text"
      @click="$router.push('/analyses/create')"
      color="accent"
      class="d-none d-md-flex"
    >
      <v-icon left>mdi-plus</v-icon>
      New Analysis
    </v-btn>
  </v-app-bar>

  <!-- Mobile Navigation Drawer -->
  <v-navigation-drawer
    v-model="drawer"
    app
    temporary
    class="d-md-none"
  >
    <v-list>
      <v-list-item
        :to="'/'"
        :active="$route.name === 'dashboard'"
        @click="drawer = false"
      >
        <v-list-item-icon>
          <v-icon>mdi-view-dashboard</v-icon>
        </v-list-item-icon>
        <v-list-item-title>Dashboard</v-list-item-title>
      </v-list-item>

      <v-list-item
        :to="'/analyses'"
        :active="$route.name === 'analysis-list'"
        @click="drawer = false"
      >
        <v-list-item-icon>
          <v-icon>mdi-format-list-bulleted</v-icon>
        </v-list-item-icon>
        <v-list-item-title>Analyses</v-list-item-title>
      </v-list-item>

      <v-list-item
        :to="'/analyses/create'"
        @click="drawer = false"
      >
        <v-list-item-icon>
          <v-icon>mdi-plus</v-icon>
        </v-list-item-icon>
        <v-list-item-title>New Analysis</v-list-item-title>
      </v-list-item>
    </v-list>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const drawer = ref(false)
</script>

<style scoped>
.v-app-bar {
  z-index: 1000;
}

.v-navigation-drawer {
  z-index: 999;
}
</style>
