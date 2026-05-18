<template>
  <v-container class="login-container" fluid>
    <div class="login-wrapper">
      <div class="login-header">
        <h1>DIC Analyzer</h1>
        <p>Вход в систему</p>
      </div>

      <div class="login-card">
        <v-form ref="form" v-model="valid" @submit.prevent="handleLogin">
          <div class="form-group">
            <label>Имя пользователя</label>
            <v-text-field
              v-model="loginData.username"
              placeholder="Введите имя пользователя"
              variant="outlined"
              density="compact"
              hide-details
              :rules="[rules.required]"
              autocomplete="username"
            />
          </div>

          <div class="form-group">
            <label>Пароль</label>
            <v-text-field
              v-model="loginData.password"
              placeholder="Введите пароль"
              variant="outlined"
              density="compact"
              hide-details
              type="password"
              :rules="[rules.required]"
              autocomplete="current-password"
            />
          </div>

          <div v-if="authError" class="error-box">
            {{ authError }}
          </div>

          <div class="button-group">
            <v-btn
              type="submit"
              block
              :loading="isLoading"
              :disabled="!valid"
              class="btn-primary"
            >
              Войти
            </v-btn>
          </div>

          <div class="text-center mt-4">
            <span class="text-link">Нет аккаунта? </span>
            <router-link to="/register" class="text-link-bold">
              Зарегистрироваться
            </router-link>
          </div>
        </v-form>
      </div>
    </div>
  </v-container>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/auth/stores/auth.store';
import type { LoginRequest } from '@/auth/types';

const router = useRouter();
const authStore = useAuthStore();

const form = ref();
const valid = ref(false);

const loginData = reactive<LoginRequest>({
  username: '',
  password: '',
});

const rules = {
  required: (v: string) => !!v || 'Обязательное поле',
};

const isLoading = computed(() => authStore.isLoading);
const authError = computed(() => authStore.error);

const handleLogin = async () => {
  const { valid: isValid } = await form.value.validate();
  if (!isValid) return;

  try {
    await authStore.login(loginData);
    router.push('/');
  } catch (err: any) {}
};
</script>

<style scoped>
.login-container {
  min-height: calc(100vh - 64px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: #c4b8a5;
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif;
}

.login-wrapper {
  width: 100%;
  max-width: 400px;
  padding: 20px;
}

.login-header {
  text-align: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #b8aa95;
}

.login-header h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2c2c2c;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 8px;
}

.login-header p {
  font-size: 0.9rem;
  color: #6b5e4a;
}

.login-card {
  background: #f0ebe0;
  border: 1px solid #b8aa95;
  padding: 24px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 0.75rem;
  font-weight: 700;
  color: #2c2c2c;
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.error-box {
  background: #fee2e2;
  border: 1px solid #b88a8a;
  color: #5c2e2e;
  padding: 10px;
  margin-bottom: 16px;
  font-size: 0.85rem;
}

.button-group {
  margin-top: 24px;
}

.btn-primary {
  background: #2c2c2c !important;
  color: #f0ebe0 !important;
  font-family: 'Montserrat', 'Arial', 'Helvetica', sans-serif !important;
  font-size: 0.85rem !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 1px !important;
  border-radius: 0 !important;
  height: 48px !important;
}

.btn-primary:hover {
  background: #1a1a1a !important;
}

.text-link {
  font-size: 0.85rem;
  color: #6b5e4a;
}

.text-link-bold {
  font-size: 0.85rem;
  color: #2c2c2c;
  font-weight: 700;
  text-decoration: none;
}

.text-link-bold:hover {
  text-decoration: underline;
}
</style>
