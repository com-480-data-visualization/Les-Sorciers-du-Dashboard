<template>
  <PageWindow :title="com.name">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">

      <!-- Category breadcrumb -->
      <div class="col-span-1 md:col-span-2 lg:col-span-3">
        <button
          @click="nav.push(`/categories/${categorySlug}`, com.name)"
          class="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
        >
          <UIcon name="i-heroicons-tag" class="size-4" />
          Category: {{ com.category }}
        </button>
      </div>

      <!-- Top importing countries -->
      <div class="bg-zinc-100 dark:bg-zinc-800 rounded-xl p-5">
        <h3 class="text-sm font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide mb-3">Top Importing Countries</h3>
        <div class="h-48">
          <D3BarChart
            :data="topImportersBar"
            :format-value="formatUsd"
            :on-bar-click="d => nav.push(`/countries/${isoFromName(d.label)}`, com.name)"
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
            :on-bar-click="d => nav.push(`/countries/${isoFromName(d.label)}`, com.name)"
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

      <!-- Share of category trade -->
      <StatCard
        title="Share of Category Trade"
        :value="formatPercent(categoryShare)"
        :subtitle="com.category"
        expandable
        clickable
      >
        <YearSlider v-model="selectedYear" />
      </StatCard>

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
import { TRADE_DATA, YEARS } from '~/utils/dummyData'
import { getCommodityById, getCommodityYearlySeries, getCategoryYearlySeries } from '~/utils/tradeExtended'
import { formatUsd, formatWeight, formatGrowth, formatPercent, categoryToSlug } from '~/utils/formatters'
import { useNavHistory } from '~/composables/useNavHistory'

definePageMeta({ layout: 'canvas' })

const route = useRoute()
const nav   = useNavHistory()

const slug = computed(() => route.params.slug as string)
const raw  = computed(() => getCommodityById(slug.value))

if (!raw.value) await navigateTo('/')

const com          = computed(() => raw.value!)
const categorySlug = computed(() => categoryToSlug(com.value.category))
const series       = computed(() => getCommodityYearlySeries(com.value))
const catSeries    = computed(() => getCategoryYearlySeries(com.value.category))

const selectedYear     = ref(YEARS.at(-1) ?? 2016)
const selectedYearData = computed(() => series.value.find(p => p.year === selectedYear.value) ?? series.value.at(-1)!)
const catYearData      = computed(() => catSeries.value.find(p => p.year === selectedYear.value) ?? catSeries.value.at(-1)!)

const growthSince1988 = computed(() => {
  const first   = series.value.at(0)
  const base    = (first?.imports.usd ?? 0) + (first?.exports.usd ?? 0)
  const current = selectedYearData.value.imports.usd + selectedYearData.value.exports.usd
  return base === 0 ? 0 : ((current - base) / base) * 100
})

const categoryShare = computed(() => {
  const catTotal = catYearData.value.imports.usd + catYearData.value.exports.usd
  const comTotal  = selectedYearData.value.imports.usd + selectedYearData.value.exports.usd
  return catTotal === 0 ? 0 : (comTotal / catTotal) * 100
})

const catImportTotal = computed(() =>
  TRADE_DATA.reduce((s, c) => s + (c.byCategory[com.value.category]?.imports.usd ?? 0), 0)
)
const catExportTotal = computed(() =>
  TRADE_DATA.reduce((s, c) => s + (c.byCategory[com.value.category]?.exports.usd ?? 0), 0)
)

const topImporters = computed(() =>
  [...TRADE_DATA]
    .map(c => {
      const catUsd  = c.byCategory[com.value.category]?.imports.usd ?? 0
      const fraction = catImportTotal.value > 0 ? com.value.imports.usd / catImportTotal.value : 0
      return { name: c.name, iso3: c.iso3, usd: Math.round(catUsd * fraction) }
    })
    .filter(c => c.usd > 0)
    .sort((a, b) => b.usd - a.usd)
    .slice(0, 5)
)
const topExporters = computed(() =>
  [...TRADE_DATA]
    .map(c => {
      const catUsd   = c.byCategory[com.value.category]?.exports.usd ?? 0
      const fraction = catExportTotal.value > 0 ? com.value.exports.usd / catExportTotal.value : 0
      return { name: c.name, iso3: c.iso3, usd: Math.round(catUsd * fraction) }
    })
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
