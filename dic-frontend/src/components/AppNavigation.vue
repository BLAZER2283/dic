<template>
  <v-app-bar app color="#2c2c2c" dark elevation="0">
    <v-app-bar-nav-icon @click="drawer = !drawer" class="d-md-none" />

    <v-toolbar-title class="d-flex align-center">
      <v-icon class="me-2" color="#e8e0d5">mdi-chart-line</v-icon>
      <span style="font-size: 1.1rem; font-weight: 700; letter-spacing: 1px;">DIC Analyzer</span>
    </v-toolbar-title>

    <v-spacer />

    <template v-if="isAuthenticated">
      <v-btn
        variant="outlined"
        href="/ucrp/"
        target="_blank"
        class="nav-btn me-2"
      >
        <v-icon left size="small">mdi-robot</v-icon>
        Plasma Optimizer
      </v-btn>

      <v-btn
        variant="flat"
        @click="$router.push('/analyses/create')"
        class="nav-btn-create me-2"
      >
        <v-icon left size="small">mdi-plus</v-icon>
        New Analysis
      </v-btn>

      <v-menu>
        <template #activator="{ props }">
          <v-btn
            variant="text"
            v-bind="props"
            class="nav-btn"
          >
            <v-icon left size="small">mdi-account</v-icon>
            {{ currentUser?.username }}
            <v-icon right size="small">mdi-chevron-down</v-icon>
          </v-btn>
        </template>
        <v-list class="menu-list">
          <v-list-item @click="handleLogout" class="menu-item">
            <v-list-item-icon>
              <v-icon size="small">mdi-logout</v-icon>
            </v-list-item-icon>
            <v-list-item-title>Выйти</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </template>

    <template v-else>
      <v-btn
        variant="outlined"
        @click="$router.push('/login')"
        class="nav-btn"
      >
        <v-icon left size="small">mdi-login</v-icon>
        Войти
      </v-btn>
    </template>

    <v-navigation-drawer
      v-model="drawer"
      app
      temporary
      class="d-md-none drawer-mobile"
    >
      <v-list>
        <template v-if="isAuthenticated">
          <v-list-item :to="'/'">
            <v-list-item-icon>
              <v-icon size="small">mdi-view-dashboard</v-icon>
            </v-list-item-icon>
            <v-list-item-title>Dashboard</v-list-item-title>
          </v-list-item>

          <v-list-item :to="'/analyses'">
            <v-list-item-icon>
              <v-icon size="small">mdi-format-list-bulleted</v-icon>
            </v-list-item-icon>
            <v-list-item-title>Analyses</v-list-item-title>
          </v-list-item>

          <v-list-item :to="'/analyses/create'">
            <v-list-item-icon>
              <v-icon size="small">mdi-plus</v-icon>
            </v-list-item-icon>
            <v-list-item-title>New Analysis</v-list-item-title>
          </v-list-item>

          <v-divider />

          <v-list-item @click="handleLogout">
            <v-list-item-icon>
              <v-icon size="small">mdi-logout</v-icon>
            </v-list-item-icon>
            <v-list-item-title>Выйти ({{ currentUser?.username }})</v-list-item-title>
          </v-list-item>
        </template>
        <template v-else>
          <v-list-item :to="'/login'">
            <v-list-item-icon>
              <v-icon size="small">mdi-login</v-icon>
            </v-list-item-icon>
            <v-list-item-title>Войти</v-list-item-title>
          </v-list-item>

          <v-list-item :to="'/register'">
            <v-list-item-icon>
              <v-icon size="small">mdi-account-plus</v-icon>
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
  border-bottom: 2px solid #1a1a1a !important;
  z-index: 1000;
}

.nav-btn {
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif !important;
  font-size: 0.8rem !important;
  text-transform: uppercase;
  letter-spacing: 1px;
  border: 1px solid #b8aa95 !important;
  background: transparent !important;
  color: #e8e0d5 !important;
}

.nav-btn:hover {
  background: #1a1a1a !important;
}

.nav-btn-create {
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif !important;
  font-size: 0.8rem !important;
  text-transform: uppercase;
  letter-spacing: 1px;
  background: #f0ebe0 !important;
  color: #2c2c2c !important;
}

.nav-btn-create:hover {
  background: #e0dacf !important;
}

.menu-list {
  background: #f0ebe0 !important;
  border: 1px solid #b8aa95 !important;
}

.menu-item {
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif;
}

.v-navigation-drawer {
  z-index: 999;
}

.drawer-mobile {
  background: #f0ebe0 !important;
}

.v-list-item-title {
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif;
}
</style>
