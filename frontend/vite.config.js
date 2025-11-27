import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    allowedHosts: true, // Allow all hosts
    hmr: false, // Disable HMR for Cloudflare Tunnel
    proxy: {
      '/api': {
        target: 'http://expressvpn:5050',
        changeOrigin: true,
      },
      '/rss-feed': {
        target: 'http://expressvpn:5050',
        changeOrigin: true,
      },
      '/static/audiobooks': {
        target: 'http://expressvpn:5050',
        changeOrigin: true,
      },
    },
  },
});
