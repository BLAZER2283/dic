<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card elevation="8">
          <v-card-title class="text-h4 font-weight-bold text-center pt-6">
            Вход в систему
          </v-card-title>

          <v-card-text class="pa-6">
            <v-form ref="form" v-model="valid" @submit.prevent="handleLogin">
              <!-- Username -->
              <v-text-field
                v-model="loginData.username"
                label="Имя пользователя"
                prepend-inner-icon="mdi-account"
                variant="outlined"
                :rules="[rules.required]"
                autocomplete="username"
                required
              />

              <!-- Password -->
              <v-text-field
                v-model="loginData.password"
                label="Пароль"
                prepend-inner-icon="mdi-lock"
                variant="outlined"
                type="password"
                :rules="[rules.required]"
                autocomplete="current-password"
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
                Войти
              </v-btn>

              <!-- Register link -->
              <div class="text-center mt-4">
                <span class="text-grey-darken-1">Нет аккаунта? </span>
                <router-link to="/register" class="text-primary text-decoration-none">
                  Зарегистрироваться
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
import { useAuthStore } from '../stores/auth.store';
import type { LoginRequest } from '../types';

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
  } catch (err: any) {
    // Error already set in store
  }
};
</script>
