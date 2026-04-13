<template>
  <div class="map-wrapper">
    <div ref="mapContainer" class="map-container"></div>

    <Transition name="fade">
      <div v-if="selectedCountry" class="big-popup-overlay" @click="selectedCountry = null">
        <CountryTradePopup @click.stop :country="selectedCountry", @close="selectedCountry = null"/>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import mapboxgl from 'mapbox-gl';
import CountryTradePopup from './CountryTradePopup.vue';
import 'mapbox-gl/dist/mapbox-gl.css';

const config = useRuntimeConfig();
const mapContainer = ref(null);
const map = ref(null);
const selectedCountry = ref(null);

onMounted(() => {
  if (process.client) {
    mapboxgl.accessToken = config.public.mapboxAccessToken;

    map.value = new mapboxgl.Map({
      container: mapContainer.value,
      style: 'mapbox://styles/mapbox/dark-v11',
      center: [0, 20],
      zoom: 2,
    });

    map.value.on('load', () => {
      // Hover logic
      map.value.on('mouseenter', 'country-label', () => {
        map.value.getCanvas().style.cursor = 'pointer';
      });

      map.value.on('mouseleave', 'country-label', () => {
        map.value.getCanvas().style.cursor = '';
      });

      // Click logic
      map.value.on('click', (e) => {
        const features = map.value.queryRenderedFeatures(e.point, {
          layers: ['country-label']
        });

        if (features.length > 0) {
          selectedCountry.value = features[0].properties.name_en || features[0].properties.name;
        }
      });
    });
  }
});

onUnmounted(() => {
  if (map.value) map.value.remove();
});
</script>

<style scoped>
.map-wrapper {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

.map-container {
  width: 100%;
  height: 100%;
}

/* Big Black Overlay */
.big-popup-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.85); /* Semi-transparent backdrop */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10;
}



/* Transition effects */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>