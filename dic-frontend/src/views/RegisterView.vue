<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card elevation="8">
          <v-card-title class="text-h4 font-weight-bold text-center pt-6">
            Регистрация
          </v-card-title>

          <v-card-text class="pa-6">
            <v-form ref="form" v-model="valid" @submit.prevent="handleRegister">
              <!-- Username -->
              <v-text-field
                v-model="registerData.username"
                label="Имя пользователя"
                prepend-inner-icon="mdi-account"
                variant="outlined"
                :rules="[rules.required, rules.minLength]"
                autocomplete="username"
                required
              />

              <!-- Email -->
              <v-text-field
                v-model="registerData.email"
                label="Email"
                prepend-inner-icon="mdi-email"
                variant="outlined"
                :rules="[rules.email]"
                type="email"
                autocomplete="email"
              />

              <!-- Password -->
              <v-text-field
                v-model="registerData.password"
                label="Пароль"
                prepend-inner-icon="mdi-lock"
                variant="outlined"
                type="password"
                :rules="[rules.required, rules.minLength8]"
                autocomplete="new-password"
                required
              />

              <!-- Confirm Password -->
              <v-text-field
                v-model="registerData.password_confirm"
                label="Подтверждение пароля"
                prepend-inner-icon="mdi-lock-check"
                variant="outlined"
                type="password"
                :rules="[rules.required, rules.passwordsMatch]"
                autocomplete="new-password"
                required
              />

              <!-- Error message -->
              <v-alert
                v-if="authError"
                type="error"
                variant="tonal"
                class="mb-4"
                density="compact"
              >
                {{ authError }}
              </v-alert>

              <!-- Submit button -->
              <v-btn
                type="submit"
                color="primary"
                size="large"
                block
                :loading="isLoading"
                :disabled="!valid"
              >
                Зарегистрироваться
              </v-btn>

              <!-- Login link -->
              <div class="text-center mt-4">
                <span class="text-grey-darken-1">Уже есть аккаунт? </span>
                <router-link to="/login" class="text-primary text-decoration-none">
                  Войти
                </router-link>
              </div>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/auth/stores/auth.store';
import type { RegisterRequest } from '@/auth/types';

const router = useRouter();
const authStore = useAuthStore();

const form = ref();
const valid = ref(false);

const registerData = reactive<RegisterRequest>({
  username: '',
  email: '',
  password: '',
  password_confirm: '',
});

const rules = {
  required: (v: string) => !!v || 'Обязательное поле',
  minLength: (v: string) => (v && v.length >= 3) || 'Минимум 3 символа',
  minLength8: (v: string) => (v && v.length >= 8) || 'Минимум 8 символов',
  email: (v: string) => !v || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) || 'Некорректный email',
  passwordsMatch: (v: string) => v === registerData.password || 'Пароли не совпадают',
};

const isLoading = computed(() => authStore.isLoading);
const authError = computed(() => authStore.error);

const handleRegister = async () => {
  const { valid: isValid } = await form.value.validate();
  if (!isValid) return;

  try {
    await authStore.register(registerData);
    router.push('/module-select');
  } catch (err: any) {
    // Error already set in store
  }
};
</script>
