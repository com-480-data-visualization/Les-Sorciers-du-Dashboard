<template>
  <div class="relative w-screen h-screen overflow-hidden bg-black">
    
    <div ref="mapContainer" class="absolute inset-0 z-0 w-full h-full" style="height: 100vh; width: 100vw;"></div>
    
    <div class="absolute inset-0 z-10 pointer-events-none">
      <slot />
    </div>

  </div>
</template>

<script setup lang="ts">
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import { TRADE_DATA, TRADE_CONNECTIONS, TRADE_FLOWS, getTradeValue, valueToColor } from '~/utils/dummyData'

// Hardcoded centroids for countries with bad/missing lat-lng in TRADE_DATA
const CENTROIDS: Record<string, [number, number]> = {
  FRA: [2.35, 46.23],
  USA: [-97.0, 38.9],
}

const getCountryLngLat = (iso3: string): [number, number] | null => {
  const key = iso3.toUpperCase()
  if (CENTROIDS[key]) return CENTROIDS[key]
  const c = TRADE_DATA.find(c => c.iso3.toUpperCase() === key)
  if (!c || (c.lat === 0 && c.lng === 0)) return null
  return [c.lng, c.lat]
}

const SPECIAL_PARTNER_COORDS: Record<string, [number, number]> = {
  WLD: [-30, 0],   // mid-Atlantic Ocean
  EUU: [10, 50],   // center of Europe
}

const getPartnerLngLat = (iso3: string): [number, number] | null => {
  if (SPECIAL_PARTNER_COORDS[iso3]) return SPECIAL_PARTNER_COORDS[iso3]
  return getCountryLngLat(iso3)
}

// Returns the TRADE_CONNECTIONS key for a hovered feature, or null if no data
const resolveConnectionKey = (geoName: string, iso3: string): string | null => {
  if (TRADE_CONNECTIONS[iso3])    return iso3
  if (TRADE_CONNECTIONS[geoName]) return geoName  // fallback for any remaining name keys
  return null
}

// Spherical interpolation → great-circle arc as [lng, lat] array
const greatCircleArc = (
  from: [number, number],
  to: [number, number],
  steps = 48
): [number, number][] => {
  const r = Math.PI / 180
  const lat1 = from[1] * r, lng1 = from[0] * r
  const lat2 = to[1] * r,   lng2 = to[0] * r
  const d = Math.acos(
    Math.max(-1, Math.min(1,
      Math.sin(lat1) * Math.sin(lat2) + Math.cos(lat1) * Math.cos(lat2) * Math.cos(lng2 - lng1)
    ))
  )
  if (d < 0.001) return [from, to]
  const pts: [number, number][] = []
  for (let i = 0; i <= steps; i++) {
    const t = i / steps
    const A = Math.sin((1 - t) * d) / Math.sin(d)
    const B = Math.sin(t * d) / Math.sin(d)
    const x = A * Math.cos(lat1) * Math.cos(lng1) + B * Math.cos(lat2) * Math.cos(lng2)
    const y = A * Math.cos(lat1) * Math.sin(lng1) + B * Math.cos(lat2) * Math.sin(lng2)
    const z = A * Math.sin(lat1) + B * Math.sin(lat2)
    pts.push([
      Math.atan2(y, x) * 180 / Math.PI,
      Math.atan2(z, Math.sqrt(x * x + y * y)) * 180 / Math.PI,
    ])
  }
  // Unwrap longitude jumps from antimeridian crossings so the path stays
  // continuous. Without this, a jump from e.g. -175 to +175 tells Mapbox to
  // render the segment the "wrong way" around the globe (appearing as a loop
  // over the pole in globe projection).
  for (let i = 1; i < pts.length; i++) {
    const cur = pts[i]!
    const prev = pts[i - 1]!
    while (cur[0] - prev[0] > 180) cur[0] -= 360
    while (cur[0] - prev[0] < -180) cur[0] += 360
  }
  return pts
}


const config = useRuntimeConfig()
const router = useRouter()
const route = useRoute()
const colorMode = useColorMode()
const isDark = computed(() => colorMode.value === 'dark')

// State for reactivity
const { showImports, showExports, metric, selectedCategory, showFlows } = useTradeState()

const mapContainer = ref<HTMLElement | null>(null)
let canvas: mapboxgl.Map

onMounted(async () => {
  if (!import.meta.client) return

  mapboxgl.accessToken = config.public.mapboxAccessToken || ''

  // Initialize Globe
  canvas = new mapboxgl.Map({
    container: mapContainer.value as HTMLElement,
    style: isDark.value ? 'mapbox://styles/mapbox/light-v11' : 'mapbox://styles/mapbox/dark-v11',
    projection: 'globe', // This creates the 3D globe effect
    center: [0, 20],
    zoom: 1.5,
    pitch: 10,
  })

  // Atmosphere and stars styling for globe
//   canvas.on('style.load', () => {
//     canvas.setFog({
//       color: 'rgb(186, 210, 235)', // Lower atmosphere
//       'high-color': 'rgb(36, 92, 223)', // Upper atmosphere
//       'horizon-blend': 0.02,
//       'space-color': 'rgb(11, 11, 25)', // Background space
//        'star-intensity': 0.6 
//     })
//   })

  canvas.on('load', async () => {
    // 1. ADD COUNTRIES LAYER
    // Ensure you have a standard geojson file at this location in your public folder
    canvas.addSource('countries', {
      type: 'geojson',
      data: '/geojson/countries.geojson',
      generateId: true
    })

    canvas.addLayer({
      id: 'country-fills',
      type: 'fill',
      source: 'countries',
      paint: {
        'fill-color': '#333333',
        'fill-opacity': 0.,
        'fill-outline-color': isDark.value ? '#111' : '#fff'
      }
    }, 'waterway-label')

    canvas.addLayer({
      id: 'country-fills-hover',
      type: 'fill',
      source: 'countries',
      paint: {
        'fill-color': '#000000',
        'fill-opacity': ['case', ['boolean', ['feature-state', 'hover'], false], 0.18, 0]
      }
    }, 'waterway-label')

    // 2. ADD FLOWS LAYER (Straight lines for simplicity to start)
    const flowFeatures = TRADE_FLOWS.map((flow, idx) => ({
      type: 'Feature',
      id: idx,
      geometry: {
        type: 'LineString',
        coordinates: [
          [flow.fromLng, flow.fromLat],
          [flow.toLng, flow.toLat]
        ]
      },
      properties: { weight: flow.weight, usd: flow.usd }
    }))

    canvas.addSource('flows', {
      type: 'geojson',
      data: { type: 'FeatureCollection', features: flowFeatures as any }
    })

    canvas.addLayer({
      id: 'flow-lines',
      type: 'line',
      source: 'flows',
      layout: { 'line-cap': 'round', 'line-join': 'round' },
      paint: {
        'line-color': '#a855f7', // Purple-500
        'line-width': ['interpolate', ['linear'], ['get', 'usd'], 0, 1, 1000000, 4],
        'line-opacity': 0, // Hidden by default
      }
    })

    // 3. ADD TRADE CONNECTION LAYERS (hover lines + endpoint circles)
    const emptyFC = { type: 'FeatureCollection' as const, features: [] }

    canvas.addSource('trade-connection-lines', { type: 'geojson', data: emptyFC })
    canvas.addSource('trade-connection-dots',  { type: 'geojson', data: emptyFC })

    const flowColor: any = ['match', ['get', 'flowType'],
      'import', '#3b82f6',
      'export', '#f97316',
      'both',   '#a855f7',
      '#888888',
    ]

    canvas.addLayer({
      id: 'trade-connection-lines',
      type: 'line',
      source: 'trade-connection-lines',
      layout: { 'line-cap': 'round', 'line-join': 'round' },
      paint: { 'line-color': flowColor, 'line-width': 2, 'line-opacity': 0.85 },
    })

    canvas.addLayer({
      id: 'trade-connection-dots',
      type: 'circle',
      source: 'trade-connection-dots',
      paint: {
        'circle-radius': 6,
        'circle-color': flowColor,
        'circle-stroke-width': 2,
        'circle-stroke-color': '#ffffff',
        'circle-opacity': 0.95,
      },
    })

    // Setup map interactions
    setupInteractions()

    // Initial color calculation
    updateMapVisuals()
  })

  // 3. REACTIVITY: Watch state and update map
  watch([showImports, showExports, metric, selectedCategory, showFlows], () => {
    if (canvas && canvas.isStyleLoaded()) {
      updateMapVisuals()
    }
  })

  // 4. READ-ONLY ON POPUPS: Watch Route
  watch(() => route.path, (newPath) => {
    if (newPath === '/') {
      canvas.dragPan.enable()
      canvas.scrollZoom.enable()
      canvas.dragRotate.enable()
    } else {
      canvas.dragPan.disable()
      canvas.scrollZoom.disable()
      canvas.dragRotate.disable()
    }
  }, { immediate: true })

  // Theme watch
  watch(colorMode, (newVal) => {
    if (canvas) {
      canvas.setStyle(newVal.value === 'dark' ? 'mapbox://styles/mapbox/dark-v11' : 'mapbox://styles/mapbox/light-v11')
      // Wait for style to load to re-add sources (omitted here for brevity, usually requires a style.load listener loop)
    }
  })
})

// --- HELPER FUNCTIONS --- //

const updateMapVisuals = () => {
  // Update Flow lines visibility
  canvas.setPaintProperty('flow-lines', 'line-opacity', showFlows.value ? 0.6 : 0)

  // Calculate Country Colors based on dummy data
  // We construct a Mapbox expression: ['match', ['get', 'iso3'], 'USA', 'rgb(x,y,z)', 'CHN', 'rgb(a,b,c)', ... , '#333']
  const colorExpression: any[] = ['match', ['get', 'ISO3166-1-Alpha-3']]

  let maxValue = 0
  
  // First, find max value for relative coloring
  TRADE_DATA.forEach(country => {
    let val = 0
    if (showImports.value) val += getTradeValue(country, 'imports', metric.value, selectedCategory.value)
    if (showExports.value) val += getTradeValue(country, 'exports', metric.value, selectedCategory.value)
    if (val > maxValue) maxValue = val
  })

  if (maxValue === 0 || (!showImports.value && !showExports.value)) {
    // Reset to default
    canvas.setPaintProperty('country-fills', 'fill-color', isDark.value ? '#3f3f46' : '#e4e4e7')
    return
  }

  // Generate color expression array
  TRADE_DATA.forEach(country => {
    let val = 0
    if (showImports.value) val += getTradeValue(country, 'imports', metric.value, selectedCategory.value)
    if (showExports.value) val += getTradeValue(country, 'exports', metric.value, selectedCategory.value)
    
    // Determine gradient type: if both are clicked, fallback to 'imports' logic for now (you can blend this later)
    const gradientType = showExports.value && !showImports.value ? 'exports' : 'imports'
    
    if (val > 0) {
      colorExpression.push(country.iso3.toUpperCase())
      colorExpression.push(valueToColor(val, maxValue, gradientType))
    }
  })

  colorExpression.push(isDark.value ? '#27272a' : '#f4f4f5') // Fallback color

  // Apply to layer
  canvas.setPaintProperty('country-fills', 'fill-color', colorExpression as any)
}

let hoveredId: number | string | null = null

const setSource = (id: string, features: any[]) => {
  (canvas.getSource(id) as mapboxgl.GeoJSONSource).setData({ type: 'FeatureCollection', features })
}

const clearTradeConnections = () => {
  setSource('trade-connection-lines', [])
  setSource('trade-connection-dots', [])
}

const updateTradeConnections = (geoName: string, iso3: string) => {
  const key = resolveConnectionKey(geoName, iso3)
  if (!key) { clearTradeConnections(); return }

  // Resolve hovered country coordinates
  const validIso3 = iso3 && iso3 !== '-99' ? iso3 : null
  let hLngLat: [number, number] | null = validIso3 ? getCountryLngLat(validIso3) : null
  if (!hLngLat) {
    const byName = TRADE_DATA.find(c => c.name === geoName)
    if (byName) {
      const k = byName.iso3.toUpperCase()
      hLngLat = CENTROIDS[k] ?? ((byName.lat !== 0 || byName.lng !== 0) ? [byName.lng, byName.lat] : null)
    }
  }
  if (!hLngLat) { clearTradeConnections(); return }

  const yearData = TRADE_CONNECTIONS[key]?.['2016']
  if (!yearData) { clearTradeConnections(); return }

  const importers = new Set(Object.keys(yearData.top3importers))
  const exporters = new Set(Object.keys(yearData.top3exportCountries))
  const allPartners = new Set([...importers, ...exporters])

  const lines: any[] = []
  const dots: any[] = []

  for (const partnerName of allPartners) {
    const partnerLngLat = getPartnerLngLat(partnerName)
    if (!partnerLngLat) continue

    const isImport = importers.has(partnerName)
    const isExport = exporters.has(partnerName)
    const flowType = isImport && isExport ? 'both' : isImport ? 'import' : 'export'

    // Circle at the partner's location, colored by flow type
    dots.push({ type: 'Feature', geometry: { type: 'Point', coordinates: partnerLngLat }, properties: { flowType } })

    // Import: arc flowing from partner → hovered country
    if (isImport) {
      const arc = greatCircleArc(partnerLngLat, hLngLat)
      lines.push({ type: 'Feature', geometry: { type: 'LineString', coordinates: arc }, properties: { flowType } })
    }

    // Export: arc flowing from hovered country → partner
    if (isExport) {
      const arc = greatCircleArc(hLngLat, partnerLngLat)
      lines.push({ type: 'Feature', geometry: { type: 'LineString', coordinates: arc }, properties: { flowType } })
    }
  }

  setSource('trade-connection-lines', lines)
  setSource('trade-connection-dots', dots)
}

const setupInteractions = () => {
  canvas.on('mousemove', 'country-fills', (e) => {
    if (route.path !== '/') return
    if (!e.features || e.features.length === 0) return

    if (hoveredId !== null) {
      canvas.setFeatureState({ source: 'countries', id: hoveredId }, { hover: false })
    }
    hoveredId = e.features[0]?.id ?? null
    if (hoveredId !== null) {
      canvas.setFeatureState({ source: 'countries', id: hoveredId }, { hover: true })
    }
    canvas.getCanvas().style.cursor = 'pointer'

    const props = e.features[0]?.properties
    if (props) updateTradeConnections(props.name ?? '', props['ISO3166-1-Alpha-3'] ?? '')
  })

  canvas.on('mouseleave', 'country-fills', () => {
    if (hoveredId !== null) {
      canvas.setFeatureState({ source: 'countries', id: hoveredId }, { hover: false })
    }
    hoveredId = null
    canvas.getCanvas().style.cursor = ''
    clearTradeConnections()
  })

  canvas.on('click', 'country-fills', (e) => {
    if (route.path !== '/') return
    if (!e.features || e.features.length === 0) return
    const properties = e.features[0]?.properties
    if (!properties) return
    const iso3 = properties['ISO3166-1-Alpha-3'] || properties.iso3 || properties.ISO_A3
    if (iso3) {
      router.push(`/countries/${iso3.toLowerCase()}`)
    }
  })
}

onUnmounted(() => {
  if (canvas) canvas.remove()
})
</script>