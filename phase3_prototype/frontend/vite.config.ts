import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['vite.svg', 'icons/icon-192x192.png', 'icons/icon-512x512.png'],
      manifest: {
        name: 'MACP Research Assistant',
        short_name: 'MACP Research',
        description: 'Multi-Agent Collaboration Protocol for AI Research',
        theme_color: '#0a0a1a',
        background_color: '#0a0a1a',
        display: 'standalone',
        scope: '/',
        start_url: '/',
        icons: [
          {
            src: '/icons/icon-192x192.png',
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: '/icons/icon-512x512.png',
            sizes: '512x512',
            type: 'image/png',
          },
          {
            src: '/icons/icon-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable',
          },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        navigateFallback: '/index.html',
        runtimeCaching: [
          {
            urlPattern: /\/api\/mcp\/agents$/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'macp-agents',
              expiration: { maxAgeSeconds: 86400 },
            },
          },
          {
            urlPattern: /\/api\/mcp\/search/,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'macp-search',
              expiration: { maxAgeSeconds: 300, maxEntries: 50 },
            },
          },
          {
            urlPattern: /\/recall/,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'macp-library',
              expiration: { maxAgeSeconds: 60 },
            },
          },
          {
            urlPattern: /\/api\/mcp\/analyze/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'macp-analyze',
              expiration: { maxAgeSeconds: 3600, maxEntries: 100 },
              networkTimeoutSeconds: 30,
            },
          },
          {
            urlPattern: /\/api\/mcp\/consensus/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'macp-consensus',
              expiration: { maxAgeSeconds: 3600, maxEntries: 50 },
            },
          },
          {
            urlPattern: /^https:\/\/cdn\.jsdelivr\.net\/.*/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'cdn-fonts',
              expiration: { maxAgeSeconds: 604800 },
            },
          },
        ],
      },
    }),
  ],
})
