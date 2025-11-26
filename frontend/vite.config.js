import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    allowedHosts: ['ytbooks.clipcast.it', 'localhost'],
    hmr: false, // Disable HMR for Cloudflare Tunnel
    proxy: {
      '/api': {
        target: 'http://flask-app:5000',
        changeOrigin: true,
      },
      '/rss-feed': {
        target: 'http://flask-app:5000',
        changeOrigin: true,
      },
      '/static/audiobooks': {
        target: 'http://flask-app:5000',
        changeOrigin: true,
      },
    },
  },
});
