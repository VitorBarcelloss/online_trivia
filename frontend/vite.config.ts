import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const serviceProxy = (target: string) => ({
  target,
  changeOrigin: true,
  rewrite: (path: string) => path.replace(/^\/api\/[^/]+/, ''),
})

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    proxy: {
      '/api/user': serviceProxy('http://localhost:8000'),
      '/api/trivia': serviceProxy('http://localhost:8001'),
      '/api/room': serviceProxy('http://localhost:8002'),
      '/api/game': serviceProxy('http://localhost:8003'),
      '/ws': {
        target: 'ws://localhost:8003',
        changeOrigin: true,
        ws: true,
        rewrite: (path: string) => path.replace(/^\/ws/, '/games'),
      },
    },
  },
})
