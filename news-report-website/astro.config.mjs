import { defineConfig } from 'astro/config'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

const projectRoot = resolve(dirname(fileURLToPath(import.meta.url)));
const repoRoot = resolve(projectRoot, '..');

// See https://docs.astro.build/reference/configuration
export default defineConfig({
  site: 'https://news-report.example.com',
  base: '/news-report/',
  trailingSlash: 'never',
  
  markdown: {
    shiki: {
      theme: 'github-dark',
      langs: ['bash', 'javascript', 'typescript', 'python', 'yaml'],
    },
  },
  
  image: {
    remotePatterns: [],
  },
  
  integrations: [],
  
  build: {
    format: 'directory',
  },

  vite: {
    server: {
      fs: {
        allow: [repoRoot],
      },
    },
  },
})
