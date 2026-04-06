<template>
  <div class="map-wrapper">
    <div ref="mapContainer" class="map-container"></div>

    <Transition name="fade">
      <div v-if="selectedCountry" class="big-popup-overlay" @click="selectedCountry = null">
        <div class="big-popup-content" @click.stop>
          <button class="close-btn" @click="selectedCountry = null">×</button>
          <h1 class="country-name">{{ selectedCountry }}</h1>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import mapboxgl from 'mapbox-gl';
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

.big-popup-content {
  background: #000;
  width: 80%;
  height: 80%;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  border: 1px solid #333;
  border-radius: 20px;
  box-shadow: 0 0 50px rgba(0,0,0,1);
}

.country-name {
  color: white;
  font-size: clamp(3rem, 10vw, 8rem); /* Responsive huge text */
  text-transform: uppercase;
  letter-spacing: 5px;
  font-weight: 900;
  margin: 0;
}

.close-btn {
  position: absolute;
  top: 30px;
  right: 40px;
  background: none;
  border: none;
  color: white;
  font-size: 3rem;
  cursor: pointer;
  line-height: 1;
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