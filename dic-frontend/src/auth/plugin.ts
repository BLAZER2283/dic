import type { App } from 'vue';
import { createPinia } from 'pinia';
import { useAuthStore } from './stores/auth.store';

/**
 * Auth Plugin - автоматическая инициализация Pinia и auth
 */
export const authPlugin = {
  install(app: App) {
    // Создаем Pinia если еще не создана
    const pinia = createPinia();
    app.use(pinia);

    // Инициализируем auth store
    const authStore = useAuthStore();
    
    // Восстанавливаем сессию при загрузке
    authStore.initAuth();
  },
};

/**
 * Helper для добавления auth guard в роутер
 */
export function setupAuthGuard(router: any) {
  router.beforeEach(async (to: any, from: any, next: any) => {
    const authStore = useAuthStore();

    // Если маршрут требует авторизации (по умолчанию все кроме requiresGuest)
    if (to.meta.requiresGuest && authStore.isAuthenticated) {
      next({ path: '/' });
    } else if (!to.meta.requiresGuest && !authStore.isAuthenticated && to.path !== '/auth' && to.path !== '/register') {
      // Неавторизованный пользователь должен идти на login
      next({ path: '/auth', query: { redirect: to.fullPath } });
    } else {
      next();
    }
  });
}
