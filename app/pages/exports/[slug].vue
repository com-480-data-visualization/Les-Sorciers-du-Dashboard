<template>
  <PageWindow :title="`${c.name} Exports`">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">

      <!-- Value in USD -->
      <StatCard
        title="Export Value (USD)"
        :value="formatUsd(selectedYearData.exports.usd)"
        color="orange"
        :subtitle="`Year: ${selectedYear}`"
        expandable
        clickable
      >
        <YearSlider v-model="selectedYear" />
      </StatCard>

      <!-- Value in weight -->
      <StatCard
        title="Export Volume (Weight)"
        :value="formatWeight(selectedYearData.exports.weight)"
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
        <p class="text-xs text-zinc-500 mt-2">
          From {{ formatUsd(series.at(0)?.exports.usd ?? 0) }} in 1988 to {{ formatUsd(selectedYearData.exports.usd) }} in {{ selectedYear }}
        </p>
      </StatCard>

      <!-- Share of world exports -->
      <StatCard
        title="Share of World Exports"
        :value="formatPercent(worldShare)"
        :subtitle="`Year: ${selectedYear}`"
        expandable
        clickable
      >
        <YearSlider v-model="selectedYear" />
      </StatCard>

      <!-- Evolution chart -->
      <div class="col-span-1 md:col-span-2 lg:col-span-3 bg-zinc-100 dark:bg-zinc-800 rounded-xl p-5">
        <h3 class="text-sm font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide mb-3">Export Evolution (1988–2023)</h3>
        <div class="h-64 w-full bg-white dark:bg-zinc-900 rounded-lg border border-zinc-200 dark:border-zinc-700 p-3">
          <D3LineChart
            :series="[
              { id: 'exports', label: 'Exports (USD)',    color: '#f97316', data: usdSeries },
              { id: 'weight',  label: 'Exports (weight)', color: '#a855f7', data: weightSeries },
            ]"
            :format-y="formatUsd"
            y-label="USD (M)"
          />
        </div>
      </div>

    </div>
  </PageWindow>
</template>

<script setup lang="ts">
import { getCountry, TRADE_DATA, YEARS } from '~/utils/dummyData'
import { getCountryYearlySeries } from '~/utils/tradeExtended'
import { formatUsd, formatWeight, formatGrowth, formatPercent } from '~/utils/formatters'
import { useNavHistory } from '~/composables/useNavHistory'

definePageMeta({ layout: 'canvas' })

const route = useRoute()
useNavHistory()

const slug = computed(() => (route.params.slug as string).toUpperCase())
const raw  = computed(() => getCountry(slug.value))

if (!raw.value) await navigateTo('/')

const c      = computed(() => raw.value!)
const series = computed(() => getCountryYearlySeries(c.value))

const selectedYear     = ref(YEARS.at(-1) ?? 2016)
const selectedYearData = computed(() => series.value.find(p => p.year === selectedYear.value) ?? series.value.at(-1)!)

const growthSince1988 = computed(() => {
  const base    = series.value.at(0)?.exports.usd ?? 0
  const current = selectedYearData.value.exports.usd
  return base === 0 ? 0 : ((current - base) / base) * 100
})

const worldShare = computed(() => {
  const worldAtYear = TRADE_DATA.reduce((sum, country) => {
    const s = getCountryYearlySeries(country).find(p => p.year === selectedYear.value)
    return sum + (s?.exports.usd ?? 0)
  }, 0)
  return worldAtYear === 0 ? 0 : (selectedYearData.value.exports.usd / worldAtYear) * 100
})

const usdSeries    = computed(() => series.value.map(p => ({ year: p.year, value: p.exports.usd })))
const weightSeries = computed(() => series.value.map(p => ({ year: p.year, value: p.exports.weight })))
</script>
