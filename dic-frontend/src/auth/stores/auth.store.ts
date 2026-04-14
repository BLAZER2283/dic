import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import AuthService from '../services/auth.service';
import type { User, LoginRequest, RegisterRequest, ChangePasswordRequest, AuthTokens } from '../types';

const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null);
  const accessToken = ref<string | null>(localStorage.getItem(ACCESS_TOKEN_KEY));
  const refreshToken = ref<string | null>(localStorage.getItem(REFRESH_TOKEN_KEY));
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const authInitialized = ref(false);

  // Getters
  // isAuthenticated = true если есть токен (даже если user ещё не загружен)
  const isAuthenticated = computed(() => !!accessToken.value);
  const currentUser = computed(() => user.value);
  const currentToken = computed(() => accessToken.value);

  // Actions
  async function login(data: LoginRequest) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await AuthService.login(data);
      setTokens(response.tokens);
      user.value = response.user;
      return response;
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Ошибка входа';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function register(data: RegisterRequest) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await AuthService.register(data);
      setTokens(response.tokens);
      user.value = response.user;
      return response;
    } catch (err: any) {
      error.value = err.response?.data || 'Ошибка регистрации';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function logout() {
    if (refreshToken.value) {
      try {
        await AuthService.logout({ refresh: refreshToken.value });
      } catch (err) {
        console.error('Logout error:', err);
      }
    }
    clearAuth();
  }

  async function fetchUser() {
    if (!accessToken.value) return;
    try {
      user.value = await AuthService.getMe();
    } catch (err) {
      console.error('Failed to fetch user:', err);
      clearAuth();
    }
  }

  async function changePassword(data: ChangePasswordRequest) {
    isLoading.value = true;
    error.value = null;
    try {
      return await AuthService.changePassword(data);
    } catch (err: any) {
      error.value = err.response?.data || 'Ошибка смены пароля';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function initAuth() {
    if (accessToken.value) {
      await fetchUser();
    }
    authInitialized.value = true;
  }

  // Helper functions
  function setTokens(tokens: AuthTokens) {
    accessToken.value = tokens.access;
    refreshToken.value = tokens.refresh;
    localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access);
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh);
  }

  function clearAuth() {
    user.value = null;
    accessToken.value = null;
    refreshToken.value = null;
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  }

  return {
    // State
    user,
    accessToken,
    refreshToken,
    isLoading,
    error,
    authInitialized,
    // Getters
    isAuthenticated,
    currentUser,
    currentToken,
    // Actions
    login,
    register,
    logout,
    fetchUser,
    changePassword,
    initAuth,
    setTokens,
    clearAuth,
  };
});
