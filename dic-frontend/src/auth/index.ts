/**
 * Auth Module - отдельный модуль для авторизации/регистрации
 * 
 * Использование:
 * 1. Добавить authRoutes в основной router
 * 2. Добавить authPlugin в app.use()
 * 3. Импортировать useAuth из этого модуля
 */

// Types
export type {
  User,
  LoginRequest,
  RegisterRequest,
  AuthTokens,
  AuthResponse,
  ChangePasswordRequest,
  LogoutRequest,
  CSRFToken,
} from './types';

// Services
export { AuthService } from './services/auth.service';
export { default as AuthServiceDefault } from './services/auth.service';

// Stores
export { useAuthStore } from './stores/auth.store';

// Composables
export { useAuth } from './composables/useAuth';

// Router
export { default as authRoutes } from './router';

// Views (для использования в основном роутере)
export { default as LoginView } from './views/LoginView.vue';
export { default as RegisterView } from './views/RegisterView.vue';
