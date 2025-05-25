import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react-swc';
import { defineConfig } from 'vite';
import tsconfigPaths from 'vite-tsconfig-paths';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss(), tsconfigPaths()],
  resolve: {
    // ensures browser compatible version of AWS JS SDK is used
    // for Amplify integration.
    alias: [
      {
        find: './runtimeConfig',
        replacement: './runtimeConfig.browser'
      }
    ]
  },
  build: {
    // https://vitejs.dev/config/build.html#chunksizewarninglimit
    chunkSizeWarningLimit: 1500,
    rollupOptions: {
      // https://rollupjs.org/guide/en/#big-list-of-options
      output: {
        // https://rollupjs.org/configuration-options/#output-compact
        compact: true
      }
    }
  }
});
