<template>
  <v-app-bar app color="primary" dark elevation="2">
    <v-app-bar-nav-icon @click="drawer = !drawer" class="d-md-none" />

    <v-toolbar-title class="d-flex align-center">
      <v-icon class="me-2">mdi-chart-line</v-icon>
      DIC Analyzer
    </v-toolbar-title>

    <v-spacer />

    <!-- Auth buttons -->
    <template v-if="isAuthenticated">
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

      <!-- User menu -->
      <v-menu>
        <template #activator="{ props }">
          <v-btn
            variant="text"
            v-bind="props"
            class="d-none d-md-flex"
          >
            <v-icon left>mdi-account</v-icon>
            {{ currentUser?.username }}
            <v-icon right>mdi-chevron-down</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item @click="handleLogout">
            <v-list-item-icon>
              <v-icon>mdi-logout</v-icon>
            </v-list-item-icon>
            <v-list-item-title>Выйти</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </template>

    <template v-else>
      <v-btn
        variant="text"
        @click="$router.push('/login')"
        class="d-none d-md-flex"
      >
        <v-icon left>mdi-login</v-icon>
        Войти
      </v-btn>
    </template>

    <!-- Mobile Navigation Drawer -->
    <v-navigation-drawer
      v-model="drawer"
      app
      temporary
      class="d-md-none"
    >
      <v-list>
        <template v-if="isAuthenticated">
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

          <v-divider />

          <v-list-item @click="handleLogout">
            <v-list-item-icon>
              <v-icon>mdi-logout</v-icon>
            </v-list-item-icon>
            <v-list-item-title>Выйти ({{ currentUser?.username }})</v-list-item-title>
          </v-list-item>
        </template>
        <template v-else>
          <v-list-item
            :to="'/login'"
            :active="$route.name === 'login'"
            @click="drawer = false"
          >
            <v-list-item-icon>
              <v-icon>mdi-login</v-icon>
            </v-list-item-icon>
            <v-list-item-title>Войти</v-list-item-title>
          </v-list-item>

          <v-list-item
            :to="'/register'"
            :active="$route.name === 'register'"
            @click="drawer = false"
          >
            <v-list-item-icon>
              <v-icon>mdi-account-plus</v-icon>
            </v-list-item-icon>
            <v-list-item-title>Регистрация</v-list-item-title>
          </v-list-item>
        </template>
      </v-list>
    </v-navigation-drawer>
  </v-app-bar>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/auth/composables/useAuth'

const drawer = ref(false)
const router = useRouter()
const { isAuthenticated, currentUser, logout } = useAuth()

const handleLogout = async () => {
  await logout()
  router.push('/login')
}
</script>

<style scoped>
.v-app-bar {
  z-index: 1000;
}

.v-navigation-drawer {
  z-index: 999;
}
</style>
