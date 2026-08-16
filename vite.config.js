import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        loja: resolve(__dirname, 'loja.html'),
        blog: resolve(__dirname, 'blog.html'),
      },
    },
  },
});
