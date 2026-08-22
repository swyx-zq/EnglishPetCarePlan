import path from 'node:path'

import { defineConfig } from 'vitest/config'

export default defineConfig({
  define: {
    ENABLE_ADJACENT_HTML: 'false',
    ENABLE_CLONE_NODE: 'false',
    ENABLE_CONTAINS: 'false',
    ENABLE_INNER_HTML: 'false',
    ENABLE_MUTATION_OBSERVER: 'false',
    ENABLE_SIZE_APIS: 'false',
    ENABLE_TEMPLATE_CONTENT: 'false',
  },
  server: {
    host: '127.0.0.1',
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    environmentOptions: {
      jsdom: {
        url: 'http://127.0.0.1/',
      },
    },
    setupFiles: ['./src/test/setup.ts'],
    include: ['src/**/*.test.{ts,tsx}'],
  },
})
