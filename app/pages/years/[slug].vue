<template>
  <PageWindow :title="String(year)">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">

      <!-- Import totals -->
      <StatCard
        title="Total Imports (USD)"
        :value="formatUsd(snapshot.totalImports.usd)"
        color="blue"
        :subtitle="formatWeight(snapshot.totalImports.weight) + ' by weight'"
      />

      <!-- Export totals -->
      <StatCard
        title="Total Exports (USD)"
        :value="formatUsd(snapshot.totalExports.usd)"
        color="orange"
        :subtitle="formatWeight(snapshot.totalExports.weight) + ' by weight'"
      />

      <!-- Difference vs another year (expandable) -->
      <StatCard
        title="Difference vs. Another Year"
        :value="formatGrowth(diffPercent)"
        :color="diffPercent >= 0 ? 'green' : 'red'"
        :subtitle="`Compared to ${compareYear}`"
        expandable
        clickable
      >
        <YearSlider v-model="compareYear" />
        <p class="text-xs text-zinc-500 mt-2">
          {{ formatUsd(compareSnapshot.totalImports.usd + compareSnapshot.totalExports.usd) }} in {{ compareYear }}
          → {{ formatUsd(snapshot.totalImports.usd + snapshot.totalExports.usd) }} in {{ year }}
        </p>
      </StatCard>

      <!-- Top import categories -->
      <div class="bg-zinc-100 dark:bg-zinc-800 rounded-xl p-5">
        <h3 class="text-sm font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide mb-3">Top Import Categories</h3>
        <div class="flex flex-col gap-2">
          <div
            v-for="cat in snapshot.topImportCategories"
            :key="cat.name"
            @click="nav.push(`/categories/${categoryToSlug(cat.name)}`, String(year))"
            class="flex items-center justify-between p-2.5 rounded-lg bg-white dark:bg-zinc-900 hover:bg-zinc-200 dark:hover:bg-zinc-700 border border-zinc-200 dark:border-zinc-700 cursor-pointer transition-colors"
          >
            <span class="text-sm font-medium text-zinc-700 dark:text-zinc-300">{{ cat.name }}</span>
            <span class="text-sm font-semibold text-blue-600 dark:text-blue-400">{{ formatUsd(cat.usd) }}</span>
          </div>
        </div>
      </div>

      <!-- Top export categories -->
      <div class="bg-zinc-100 dark:bg-zinc-800 rounded-xl p-5">
        <h3 class="text-sm font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide mb-3">Top Export Categories</h3>
        <div class="flex flex-col gap-2">
          <div
            v-for="cat in snapshot.topExportCategories"
            :key="cat.name"
            @click="nav.push(`/categories/${categoryToSlug(cat.name)}`, String(year))"
            class="flex items-center justify-between p-2.5 rounded-lg bg-white dark:bg-zinc-900 hover:bg-zinc-200 dark:hover:bg-zinc-700 border border-zinc-200 dark:border-zinc-700 cursor-pointer transition-colors"
          >
            <span class="text-sm font-medium text-zinc-700 dark:text-zinc-300">{{ cat.name }}</span>
            <span class="text-sm font-semibold text-orange-600 dark:text-orange-400">{{ formatUsd(cat.usd) }}</span>
          </div>
        </div>
      </div>

      <!-- Top importing countries -->
      <div class="bg-zinc-100 dark:bg-zinc-800 rounded-xl p-5">
        <h3 class="text-sm font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide mb-3">Top Importing Countries</h3>
        <div class="flex flex-col gap-2">
          <div
            v-for="c in snapshot.topImportCountries"
            :key="c.iso3"
            @click="nav.push(`/countries/${c.iso3.toLowerCase()}`, String(year))"
            class="flex items-center justify-between p-2.5 rounded-lg bg-white dark:bg-zinc-900 hover:bg-zinc-200 dark:hover:bg-zinc-700 border border-zinc-200 dark:border-zinc-700 cursor-pointer transition-colors"
          >
            <span class="text-sm font-medium text-zinc-700 dark:text-zinc-300">{{ c.name }}</span>
            <span class="text-sm font-semibold text-blue-600 dark:text-blue-400">{{ formatUsd(c.usd) }}</span>
          </div>
        </div>
      </div>

      <!-- Top exporting countries -->
      <div class="bg-zinc-100 dark:bg-zinc-800 rounded-xl p-5">
        <h3 class="text-sm font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide mb-3">Top Exporting Countries</h3>
        <div class="flex flex-col gap-2">
          <div
            v-for="c in snapshot.topExportCountries"
            :key="c.iso3"
            @click="nav.push(`/countries/${c.iso3.toLowerCase()}`, String(year))"
            class="flex items-center justify-between p-2.5 rounded-lg bg-white dark:bg-zinc-900 hover:bg-zinc-200 dark:hover:bg-zinc-700 border border-zinc-200 dark:border-zinc-700 cursor-pointer transition-colors"
          >
            <span class="text-sm font-medium text-zinc-700 dark:text-zinc-300">{{ c.name }}</span>
            <span class="text-sm font-semibold text-orange-600 dark:text-orange-400">{{ formatUsd(c.usd) }}</span>
          </div>
        </div>
      </div>

      <!-- Historical note -->
      <div class="col-span-1 md:col-span-2 lg:col-span-3 bg-zinc-100 dark:bg-zinc-800 rounded-xl p-5">
        <h3 class="text-sm font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide mb-3">
          Historical Context
        </h3>
        <p class="text-zinc-700 dark:text-zinc-300 leading-relaxed">{{ snapshot.historicalNote }}</p>
      </div>

    </div>
  </PageWindow>
</template>

<script setup lang="ts">
import { YEARS } from '~/utils/dummyData'
import { getYearSnapshot } from '~/utils/tradeExtended'
import { formatUsd, formatWeight, formatGrowth, categoryToSlug } from '~/utils/formatters'
import { useNavHistory } from '~/composables/useNavHistory'

definePageMeta({ layout: 'canvas' })

const route = useRoute()
const nav   = useNavHistory()

const year = computed(() => parseInt(route.params.slug as string))

if (!YEARS.includes(year.value)) await navigateTo('/')

const snapshot = computed(() => getYearSnapshot(year.value))

const compareYear     = ref(year.value > (YEARS[0] ?? 1988) ? year.value - 1 : (YEARS[1] ?? 1989))
const compareSnapshot = computed(() => getYearSnapshot(compareYear.value))

const diffPercent = computed(() => {
  const current = snapshot.value.totalImports.usd + snapshot.value.totalExports.usd
  const compare = compareSnapshot.value.totalImports.usd + compareSnapshot.value.totalExports.usd
  return compare === 0 ? 0 : ((current - compare) / compare) * 100
})
</script>
