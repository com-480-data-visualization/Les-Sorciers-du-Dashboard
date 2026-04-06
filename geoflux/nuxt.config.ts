// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  runtimeConfig: {
    public: {
      // If NUXT_PUBLIC_MAPBOX_ACCESS_TOKEN exists in .env, 
      // Nuxt automatically assigns it here if empty or use a placeholder.
      mapboxAccessToken: '', 
    }
  }
})
