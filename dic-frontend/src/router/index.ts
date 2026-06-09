import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '@/views/DashboardView.vue'
import ModuleSelectView from '@/views/ModuleSelectView.vue'
import AnalysisListView from '@/views/AnalysisListView.vue'
import AnalysisCreateView from '@/views/AnalysisCreateView.vue'
import AnalysisDetailView from '@/views/AnalysisDetailView.vue'

// Импортируем auth маршруты из отдельного модуля
import authRoutes from '@/auth/router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // Auth маршруты из отдельного модуля
    ...authRoutes,
    
    // Главная страница — выбор модуля
    {
      path: '/',
      name: 'module-select',
      component: ModuleSelectView,
      meta: { title: 'Выбор модуля', requiresAuth: true }
    },

    // Основные маршруты приложения
    {
      path: '/dic',
      name: 'dashboard',
      component: DashboardView,
      meta: { title: 'Dashboard', requiresAuth: true }
    },
    {
      path: '/analyses',
      name: 'analysis-list',
      component: AnalysisListView,
      meta: { title: 'Analyses', requiresAuth: true }
    },
    {
      path: '/analyses/create',
      name: 'analysis-create',
      component: AnalysisCreateView,
      meta: { title: 'Create Analysis', requiresAuth: true }
    },
    {
      path: '/analyses/:id',
      name: 'analysis-detail',
      component: AnalysisDetailView,
      meta: { title: 'Analysis Detail', requiresAuth: true }
    }
  ]
})

// Update page title
router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title} - DIC Analyzer`
  next()
})

export default router
