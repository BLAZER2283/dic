import { useAuthStore } from '../stores/auth.store';
import { storeToRefs } from 'pinia';

/**
 * Composable для удобного использования auth в компонентах
 */
export function useAuth() {
  const authStore = useAuthStore();
  const { isAuthenticated, currentUser, currentToken, isLoading, error, authInitialized } = storeToRefs(authStore);

  return {
    // State
    isAuthenticated,
    currentUser,
    currentToken,
    isLoading,
    error,
    authInitialized,
    // Actions
    login: authStore.login,
    register: authStore.register,
    logout: authStore.logout,
    changePassword: authStore.changePassword,
    initAuth: authStore.initAuth,
  };
}
