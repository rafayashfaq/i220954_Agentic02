import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/auth': 'http://127.0.0.1:8000',
      '/jobs': 'http://127.0.0.1:8000',
      '/proposals': 'http://127.0.0.1:8000',
      '/approvals': 'http://127.0.0.1:8000',
      '/messages': 'http://127.0.0.1:8000',
      '/runs': 'http://127.0.0.1:8000',
      '/analytics': 'http://127.0.0.1:8000',
      '/settings': 'http://127.0.0.1:8000',
      '/health': 'http://127.0.0.1:8000',
    },
  },
});

