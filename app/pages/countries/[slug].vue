<template>
  <PageWindow :title="c.name">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">

      <!-- Commercial balance -->
      <StatCard title="Commercial Balance" :value="formatUsd(balance)" :color="balance >= 0 ? 'orange' : 'blue'" subtitle="Total Exports − Total Imports" />

      <!-- Total imports (clickable → imports page) -->
      <StatCard
        title="Total Imports"
        :value="formatUsd(c.imports.usd)"
        color="blue"
        :subtitle="formatWeight(c.imports.weight) + ' by weight'"
        clickable
        @click="nav.push(`/imports/${slug}`, c.name)"
      >
        <div class="flex items-center gap-2 mt-2 text-blue-600 dark:text-blue-400 text-sm font-medium">
          View import breakdown
          <UIcon name="i-heroicons-arrow-right" class="size-4" />
        </div>
      </StatCard>

      <!-- Total exports (clickable → exports page) -->
      <StatCard
        title="Total Exports"
        :value="formatUsd(c.exports.usd)"
        color="orange"
        :subtitle="formatWeight(c.exports.weight) + ' by weight'"
        clickable
        @click="nav.push(`/exports/${slug}`, c.name)"
      >
        <div class="flex items-center gap-2 mt-2 text-orange-600 dark:text-orange-400 text-sm font-medium">
          View export breakdown
          <UIcon name="i-heroicons-arrow-right" class="size-4" />
        </div>
      </StatCard>

      <!-- Category pie chart (expandable) -->
      <div
        :class="[
          'rounded-xl p-5 flex flex-col gap-3 transition-all duration-300 cursor-pointer',
          'bg-zinc-100 dark:bg-zinc-800',
          pieExpanded ? 'md:col-span-2 lg:col-span-3' : 'col-span-1',
        ]"
        @click="pieExpanded = !pieExpanded"
      >
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide">Category Breakdown</h3>
          <UIcon :name="pieExpanded ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'" class="size-4 text-zinc-400" />
        </div>

        <div :class="['w-full transition-all duration-300', pieExpanded ? 'h-80' : 'h-44']">
          <D3PieChart
            :slices="pieSlices"
            :on-slice-click="pieExpanded ? onCategoryClick : undefined"
          />
        </div>

        <p v-if="pieExpanded" class="text-xs text-zinc-500 dark:text-zinc-400 text-center">
          Click a slice to open its category page
        </p>
      </div>

      <!-- Top 3 import sources -->
      <StatCard title="Top 3 Import Sources" color="blue" subtitle="share of total imports">
        <div v-if="tradeConnections" class="flex flex-col gap-2 mt-1">
          <div
            v-for="(pct, country) in tradeConnections.top3importers"
            :key="country"
            class="flex items-center justify-between"
          >
            <span class="text-sm text-zinc-700 dark:text-zinc-300">{{ iso3ToName(country) }}</span>
            <span class="text-sm font-semibold text-blue-600 dark:text-blue-400">{{ pct.toFixed(1) }}%</span>
          </div>
        </div>
        <p v-else class="text-sm text-zinc-400 mt-1">No data available</p>
      </StatCard>

      <!-- Top 3 export destinations -->
      <StatCard title="Top 3 Export Destinations" color="orange" subtitle="share of total exports">
        <div v-if="tradeConnections" class="flex flex-col gap-2 mt-1">
          <div
            v-for="(pct, country) in tradeConnections.top3exportCountries"
            :key="country"
            class="flex items-center justify-between"
          >
            <span class="text-sm text-zinc-700 dark:text-zinc-300">{{ iso3ToName(country) }}</span>
            <span class="text-sm font-semibold text-orange-600 dark:text-orange-400">{{ pct.toFixed(1) }}%</span>
          </div>
        </div>
        <p v-else class="text-sm text-zinc-400 mt-1">No data available</p>
      </StatCard>
      
      <!-- Evolution over time -->
      <div class="col-span-1 md:col-span-2 lg:col-span-3 bg-zinc-100 dark:bg-zinc-800 rounded-xl p-5">
        <h3 class="text-sm font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide mb-3">Evolution Over Time</h3>
        <div class="h-64 w-full bg-white dark:bg-zinc-900 rounded-lg border border-zinc-200 dark:border-zinc-700 p-3">
          <D3LineChart :series="evolutionSeries" :format-y="formatUsd" y-label="USD (M)" />
        </div>
      </div>

    </div>
  </PageWindow>
</template>

<script setup lang="ts">
import { getCountry, getTradeConnections, iso3ToName } from '~/utils/dummyData'
import { getCountryYearlySeries } from '~/utils/tradeExtended'
import { formatUsd, formatWeight, categoryToSlug } from '~/utils/formatters'
import { useNavHistory } from '~/composables/useNavHistory'
import type { PieSlice } from '~/components/d3/PieChart.vue'

definePageMeta({ layout: 'canvas' })

const route = useRoute()
const nav   = useNavHistory()

const slug = computed(() => (route.params.slug as string).toUpperCase())
const raw  = computed(() => getCountry(slug.value))

if (!raw.value) await navigateTo('/')

// Non-null alias used in template — safe after the redirect above
const c = computed(() => raw.value!)

const balance = computed(() => c.value.exports.usd - c.value.imports.usd)

const CATEGORY_COLORS = [
  '#3b82f6','#f97316','#22c55e','#a855f7','#eab308',
  '#06b6d4','#ec4899','#f43f5e','#10b981','#8b5cf6',
  '#f59e0b','#6366f1',
]

const pieSlices = computed<PieSlice[]>(() => {
  const all = Object.entries(c.value.byCategory)
    .map(([cat, data]) => ({
      id: cat, label: cat,
      value: (data?.imports.usd ?? 0) + (data?.exports.usd ?? 0),
    }))
    .filter(s => s.value > 0)
    .sort((a, b) => b.value - a.value)

  const top = all.slice(0, 11).map((s, i) => ({ ...s, color: CATEGORY_COLORS[i % CATEGORY_COLORS.length] }))

  if (all.length <= 11) return top

  const otherValue = all.slice(11).reduce((sum, s) => sum + s.value, 0)
  return [...top, { id: '__other__', label: 'Other', value: otherValue, color: '#9ca3af' }]
})

const pieExpanded = ref(false)

function onCategoryClick(slice: PieSlice) {
  if (slice.id === '__other__') return
  nav.push(`/categories/${categoryToSlug(slice.id)}`, c.value.name)
}

const tradeConnections = computed(() => getTradeConnections(c.value.iso3, '2016'))

const yearlySeries = computed(() => getCountryYearlySeries(c.value))

const evolutionSeries = computed(() => [
  { id: 'imports', label: 'Imports', color: '#3b82f6', data: yearlySeries.value.map(p => ({ year: p.year, value: p.imports.usd })) },
  { id: 'exports', label: 'Exports', color: '#f97316', data: yearlySeries.value.map(p => ({ year: p.year, value: p.exports.usd })) },
])
</script>
