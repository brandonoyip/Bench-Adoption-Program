import { defineConfig } from 'vite';
export default defineConfig({build:{rollupOptions:{output:{manualChunks:{map:['leaflet'],database:['@supabase/supabase-js']}}}}});
