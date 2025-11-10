import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3001,
    proxy: {
      '/api': {
        target: 'http://localhost:7531',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:7531',
        ws: true,
      },
    },
  },
})

