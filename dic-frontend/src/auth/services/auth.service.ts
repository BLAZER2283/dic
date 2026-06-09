import axios from 'axios';
import type {
  User,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  ChangePasswordRequest,
  LogoutRequest,
  CSRFToken,
  AuthTokens,
} from '../types';

const ACCESS_TOKEN_KEY = 'access_token';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor для добавления Bearer токена
api.interceptors.request.use((config) => {
  const token = localStorage.getItem(ACCESS_TOKEN_KEY);
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

// Interceptor для добавления CSRF токена
api.interceptors.request.use(async (config) => {
  const methodsThatNeedCsrf = ['POST', 'PUT', 'PATCH', 'DELETE'];
  if (methodsThatNeedCsrf.includes(config.method?.toUpperCase() || '')) {
    try {
      const response = await axios.get<CSRFToken>('/api/auth/get-csrf-token/');
      const csrfToken = response.data.csrfToken;

      if (config.data instanceof FormData) {
        config.data.append('csrfmiddlewaretoken', csrfToken);
      } else {
        config.headers['X-CSRFToken'] = csrfToken;
      }
    } catch (error) {
      console.error('Failed to fetch CSRF token:', error);
    }
  }
  return config;
});

export class AuthService {
  /**
   * Регистрация нового пользователя
   */
  static async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/register/', data);
    return response.data;
  }

  /**
   * Вход пользователя
   */
  static async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/login/', data);
    return response.data;
  }

  /**
   * Выход пользователя
   */
  static async logout(data: LogoutRequest): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>('/auth/logout/', data);
    return response.data;
  }

  /**
   * Получение данных текущего пользователя
   */
  static async getMe(): Promise<User> {
    const response = await api.get<User>('/auth/me/');
    return response.data;
  }

  /**
   * Смена пароля
   */
  static async changePassword(data: ChangePasswordRequest): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>('/auth/change-password/', data);
    return response.data;
  }

  /**
   * Получение CSRF токена
   */
  static async getCsrfToken(): Promise<CSRFToken> {
    const response = await api.get<CSRFToken>('/auth/get-csrf-token/');
    return response.data;
  }
}

export default AuthService;
