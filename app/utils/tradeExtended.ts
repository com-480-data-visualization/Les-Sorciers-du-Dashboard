import commoditiesRaw from '~/utils/generated/commodities.json'
import categoriesRaw  from '~/utils/generated/categories.json'
import yearsRaw       from '~/utils/generated/years.json'
import type { CountryTrade, YearlyPoint } from '~/utils/dummyData'

// ─── Types ─────────────────────────────────────────────────────────────────

export interface Commodity {
  id:        string   // same as comm_code, used in URL slug
  comm_code: string
  name:      string
  category:  string
  imports:   { usd: number; weight: number }
  exports:   { usd: number; weight: number }
  series:    YearlyPoint[]
}

interface CategoryEntry {
  id:      string
  code:    string
  name:    string
  imports: { usd: number; weight: number }
  exports: { usd: number; weight: number }
  series:  YearlyPoint[]
}

interface YearEntry {
  year:                number
  imports:             { usd: number; weight: number }
  exports:             { usd: number; weight: number }
  topImportCategories: Array<{ id: string; name: string; usd: number }>
  topExportCategories: Array<{ id: string; name: string; usd: number }>
  topImportCountries:  Array<{ iso3: string; name: string; usd: number }>
  topExportCountries:  Array<{ iso3: string; name: string; usd: number }>
  historicalNote:      string
}

export interface YearSnapshot {
  totalImports:         { usd: number; weight: number }
  totalExports:         { usd: number; weight: number }
  topImportCategories:  Array<{ name: string; usd: number }>
  topExportCategories:  Array<{ name: string; usd: number }>
  topImportCountries:   Array<{ iso3: string; name: string; usd: number }>
  topExportCountries:   Array<{ iso3: string; name: string; usd: number }>
  historicalNote:       string
}

// ─── Data ──────────────────────────────────────────────────────────────────

export const COMMODITIES: Commodity[] = commoditiesRaw as unknown as Commodity[]

const CATEGORIES_DATA: CategoryEntry[] = categoriesRaw as unknown as CategoryEntry[]
const YEARS_DATA: YearEntry[]          = yearsRaw      as unknown as YearEntry[]

// ─── Lookups ───────────────────────────────────────────────────────────────

export function getCommodityById(id: string): Commodity | undefined {
  return COMMODITIES.find(c => c.id === id)
}

export function getCommoditiesByCategory(category: string): Commodity[] {
  return COMMODITIES.filter(c => c.category === category)
}

export function getCountryYearlySeries(country: CountryTrade): YearlyPoint[] {
  return country.series
}

export function getCategoryYearlySeries(category: string): YearlyPoint[] {
  return CATEGORIES_DATA.find(c => c.name === category)?.series ?? []
}

export function getCommodityYearlySeries(commodity: Commodity): YearlyPoint[] {
  return commodity.series
}

export function getYearSnapshot(year: number): YearSnapshot {
  const entry = YEARS_DATA.find(y => y.year === year)
  if (!entry) {
    return {
      totalImports: { usd: 0, weight: 0 },
      totalExports: { usd: 0, weight: 0 },
      topImportCategories: [],
      topExportCategories: [],
      topImportCountries: [],
      topExportCountries: [],
      historicalNote: '',
    }
  }
  return {
    totalImports:        entry.imports,
    totalExports:        entry.exports,
    topImportCategories: entry.topImportCategories,
    topExportCategories: entry.topExportCategories,
    topImportCountries:  entry.topImportCountries,
    topExportCountries:  entry.topExportCountries,
    historicalNote:      entry.historicalNote,
  }
}
