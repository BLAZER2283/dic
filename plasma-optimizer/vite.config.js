import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  base: '/ucrp/',
  plugins: [react()],
  server: {
    port: 3000,
    open: true,
    proxy: {
      '/api/ucrp': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/ucrp/, '/api/ucrp'),
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  }
})