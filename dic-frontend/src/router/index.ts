import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '@/views/DashboardView.vue'
import AnalysisListView from '@/views/AnalysisListView.vue'
import AnalysisCreateView from '@/views/AnalysisCreateView.vue'
import AnalysisDetailView from '@/views/AnalysisDetailView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView,
      meta: { title: 'Dashboard' }
    },
    {
      path: '/analyses',
      name: 'analysis-list',
      component: AnalysisListView,
      meta: { title: 'Analyses' }
    },
    {
      path: '/analyses/create',
      name: 'analysis-create',
      component: AnalysisCreateView,
      meta: { title: 'Create Analysis' }
    },
    {
      path: '/analyses/:id',
      name: 'analysis-detail',
      component: AnalysisDetailView,
      meta: { title: 'Analysis Detail' }
    }
  ]
})

// Update page title
router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title} - DIC Analyzer`
  next()
})

export default router
