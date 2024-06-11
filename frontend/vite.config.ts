import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  build: {
    sourcemap: true, // Sørg for, at sourcemap er sat til true
  },
  server: {
    // port: 3000, // Juster porten, hvis det er nødvendigt
    open: true, // Åbn browseren automatisk ved start
  },
})
