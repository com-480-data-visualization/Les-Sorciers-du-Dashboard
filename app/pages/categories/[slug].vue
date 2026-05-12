<template>
  <PageWindow :title="category">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">

      <!-- Top importing countries -->
      <div class="bg-zinc-100 dark:bg-zinc-800 rounded-xl p-5">
        <h3 class="text-sm font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide mb-3">Top Importing Countries</h3>
        <div class="h-48">
          <D3BarChart
            :data="topImportersBar"
            :format-value="formatUsd"
            :on-bar-click="d => nav.push(`/countries/${isoFromName(d.label)}`, category)"
          />
        </div>
      </div>

      <!-- Top exporting countries -->
      <div class="bg-zinc-100 dark:bg-zinc-800 rounded-xl p-5">
        <h3 class="text-sm font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide mb-3">Top Exporting Countries</h3>
        <div class="h-48">
          <D3BarChart
            :data="topExportersBar"
            :format-value="formatUsd"
            :on-bar-click="d => nav.push(`/countries/${isoFromName(d.label)}`, category)"
          />
        </div>
      </div>

      <!-- Value in USD -->
      <StatCard
        title="Trade Value (USD)"
        :value="formatUsd(selectedYearData.imports.usd + selectedYearData.exports.usd)"
        :subtitle="`Year: ${selectedYear}`"
        expandable
        clickable
      >
        <YearSlider v-model="selectedYear" />
      </StatCard>

      <!-- Value in weight -->
      <StatCard
        title="Trade Volume (Weight)"
        :value="formatWeight(selectedYearData.imports.weight + selectedYearData.exports.weight)"
        :subtitle="`Year: ${selectedYear}`"
        expandable
        clickable
      >
        <YearSlider v-model="selectedYear" />
      </StatCard>

      <!-- Growth since 1988 -->
      <StatCard
        title="Growth Since 1988"
        :value="formatGrowth(growthSince1988)"
        :color="growthSince1988 >= 0 ? 'green' : 'red'"
        subtitle="Base year: 1988"
        expandable
        clickable
      >
        <YearSlider v-model="selectedYear" />
      </StatCard>

      <!-- Share of world trade -->
      <StatCard
        title="Share of World Trade"
        :value="formatPercent(worldShare)"
        :subtitle="`Year: ${selectedYear}`"
        expandable
        clickable
      >
        <YearSlider v-model="selectedYear" />
      </StatCard>

      <!-- Commodities in this category -->
      <div class="col-span-1 md:col-span-2 bg-zinc-100 dark:bg-zinc-800 rounded-xl p-5">
        <h3 class="text-sm font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide mb-3">Commodities</h3>
        <div class="grid grid-cols-2 gap-2">
          <div
            v-for="com in commodities"
            :key="com.id"
            @click="nav.push(`/commodities/${com.id}`, category)"
            class="p-3 rounded-lg bg-white dark:bg-zinc-900 hover:bg-zinc-200 dark:hover:bg-zinc-700 border border-zinc-200 dark:border-zinc-700 cursor-pointer transition-colors"
          >
            <p class="font-medium text-zinc-800 dark:text-zinc-200 text-sm">{{ com.name }}</p>
            <p class="text-xs text-zinc-500 mt-1">{{ formatUsd(com.imports.usd + com.exports.usd) }} total</p>
          </div>
        </div>
      </div>

      <!-- Evolution chart -->
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
import { TRADE_DATA, CATEGORIES, YEARS } from '~/utils/dummyData'
import { getCategoryYearlySeries, getCommoditiesByCategory } from '~/utils/tradeExtended'
import { formatUsd, formatWeight, formatGrowth, formatPercent, slugToCategory } from '~/utils/formatters'
import { useNavHistory } from '~/composables/useNavHistory'

definePageMeta({ layout: 'canvas' })

const route = useRoute()
const nav   = useNavHistory()

const slug     = computed(() => route.params.slug as string)
const category = computed(() => slugToCategory(slug.value, CATEGORIES) ?? slug.value)

if (!slugToCategory(slug.value, CATEGORIES)) await navigateTo('/')

const commodities      = computed(() => getCommoditiesByCategory(category.value))
const series           = computed(() => getCategoryYearlySeries(category.value))
const selectedYear     = ref(YEARS.at(-1) ?? 2016)
const selectedYearData = computed(() => series.value.find(p => p.year === selectedYear.value) ?? series.value.at(-1)!)

const growthSince1988 = computed(() => {
  const first   = series.value.at(0)
  const base    = (first?.imports.usd ?? 0) + (first?.exports.usd ?? 0)
  const current = selectedYearData.value.imports.usd + selectedYearData.value.exports.usd
  return base === 0 ? 0 : ((current - base) / base) * 100
})

const worldShare = computed(() => {
  const worldTotal = TRADE_DATA.reduce((s, c) => s + c.imports.usd + c.exports.usd, 0)
  const catTotal   = selectedYearData.value.imports.usd + selectedYearData.value.exports.usd
  return worldTotal === 0 ? 0 : (catTotal / worldTotal) * 100
})

const topImporters = computed(() =>
  [...TRADE_DATA]
    .map(c => ({ name: c.name, iso3: c.iso3, usd: c.byCategory[category.value]?.imports.usd ?? 0 }))
    .filter(c => c.usd > 0)
    .sort((a, b) => b.usd - a.usd)
    .slice(0, 5)
)
const topExporters = computed(() =>
  [...TRADE_DATA]
    .map(c => ({ name: c.name, iso3: c.iso3, usd: c.byCategory[category.value]?.exports.usd ?? 0 }))
    .filter(c => c.usd > 0)
    .sort((a, b) => b.usd - a.usd)
    .slice(0, 5)
)

const topImportersBar = computed(() => topImporters.value.map(c => ({ label: c.name, value: c.usd, color: '#3b82f6' })))
const topExportersBar = computed(() => topExporters.value.map(c => ({ label: c.name, value: c.usd, color: '#f97316' })))

function isoFromName(name: string): string {
  return TRADE_DATA.find(c => c.name === name)?.iso3.toLowerCase() ?? ''
}

const evolutionSeries = computed(() => [
  { id: 'imports', label: 'Imports', color: '#3b82f6', data: series.value.map(p => ({ year: p.year, value: p.imports.usd })) },
  { id: 'exports', label: 'Exports', color: '#f97316', data: series.value.map(p => ({ year: p.year, value: p.exports.usd })) },
])
</script>
