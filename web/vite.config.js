import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',  // WSL에서 Windows 접근 허용
    port: 5173,
    strictPort: false,
  }
})

